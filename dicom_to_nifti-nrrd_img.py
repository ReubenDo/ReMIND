import os
import argparse
from tqdm import tqdm
import SimpleITK as sitk
from natsort import natsorted
import pydicom

TIMES = ['Preop', 'Intraop']

def parsing_data():
    parser = argparse.ArgumentParser(
        description='Conversion DICOM images from TCIA into NIFTI/NRRD')
    parser.add_argument('--path_dicom',
                        type=str,
                        default='../../data/ReMIND_TCIA/manifest-1695134609823/ReMIND/',
                        help='Path to the DICOM iamges from TCIA')
    parser.add_argument('--path_output',
                        type=str,
                        default='./nifti_imgs',
                        help='Path to the output NIfTI image dataset')
    parser.add_argument('--nrrd',
                        action='store_true',
                        help='Convert to NRRD format')
    parser.add_argument('--nifti',
                        action='store_true',
                        help='Convert to NIfTI format')
    opt = parser.parse_args()

    return opt


def get_filename(dicom_input_path):
    dicom_input = pydicom.read_file(dicom_input_path)
    base_filename = ""
    # noinspection PyBroadException
    try:
        # construct the filename 
        base_filename = ""
        if 'SeriesNumber' in dicom_input:
            base_filename = f'{dicom_input.SeriesNumber}'
            if 'SeriesDescription' in dicom_input:
                base_filename = '%s_%s' % (base_filename, dicom_input.SeriesDescription)
            elif 'SequenceName' in dicom_input[0]:
                base_filename = '%s_%s' % (base_filename,dicom_input.SequenceName)
            elif 'ProtocolName' in dicom_input[0]:
                base_filename = '%s_%s' % (base_filename, dicom_input.ProtocolName)
        else:
            base_filename = dicom_input[0].SeriesInstanceUID
    except:
        print("Unable to convert: %s" % dicom_input)
    return base_filename


def main():
    opt = parsing_data()
    if opt.nrrd:
        ext = 'nrrd'
    elif opt.nifti:
        ext = 'nii.gz'
    else:
        raise Exception('Either --nrrd or --nifti are required'
        )
    cases = natsorted([k for k in os.listdir(opt.path_dicom) if os.path.isdir(os.path.join(opt.path_dicom,k))])
    number_imgs = {t:0 for t in TIMES}
    print(f"Found {len(cases)} cases.")
    for case in tqdm(cases):
        path_case = os.path.join(opt.path_dicom, case)
        path_output_case = os.path.join(opt.path_output, case)
        
        for acquisition_time in TIMES:
            sessions = [k for k in os.listdir(path_case) if acquisition_time in k]
            assert len(sessions)>0, f'Error with {case} - cannot found {acquisition_time} folder'
            assert len(sessions)==1, f'Error with {case} - found more than 1 {acquisition_time} folder'
            session = sessions[0]
            
            path_case_session = os.path.join(path_case, session)
            path_output_case_session = os.path.join(path_output_case, session)
            os.makedirs(path_output_case_session, exist_ok=True)
            
            dicom_folders = [k for k in os.listdir(path_case_session) \
                            if os.path.isdir(os.path.join(path_case_session, k)) 
                            and not 'seg' in k]
            
            # Iterates over all images files in the session
            for dicom_folder in dicom_folders:
                # Load DICOM as SITK Image
                reader = sitk.ImageSeriesReader()
                dicom_names = reader.GetGDCMSeriesFileNames(os.path.join(path_case_session, dicom_folder))
                reader.SetFileNames(dicom_names)      
                image = reader.Execute()
                
                # Output filename 
                filename = get_filename(dicom_names[0])

                # Conversion
                if opt.nifti:
                    sitk.WriteImage(image, os.path.join(path_output_case_session,f'{filename}.nii.gz'), 
                                                        useCompression=True
                    )
                elif opt.nrrd: # Errors where found if using NRRD IO in SITK
                    temp_file = os.path.join(path_output_case_session, 'temp.nii.gz')
                    output_file = os.path.join(path_output_case_session,f'{filename}.nrrd')
                    sitk.WriteImage(image, temp_file, useCompression=True)
                    image = sitk.ReadImage(temp_file)
                    sitk.WriteImage(image, output_file, useCompression=True)
                    os.remove(temp_file)
                number_imgs[acquisition_time]+=1
            
    
    for t in TIMES:
        print(f"Number of {t} scans: {number_imgs[t]}")

if __name__ == '__main__':
    main()

            
            
        