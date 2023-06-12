import os
from tqdm import tqdm
from natsort import natsorted
import subprocess
import json
import argparse


def parsing_data():
    parser = argparse.ArgumentParser(
        description='Conversion NRRD SEG into DICOM SEG')
    parser.add_argument('--path_nrrd',
                        type=str,
                        default='./nrrd',
                        help='Path to the input NRRD dataset')
    parser.add_argument('--path_dicom',
                        type=str,
                        default='./dicom_folder',
                        help='Path to the output DICOM dataset')
    parser.add_argument('--img2seg',
                        type=str,
                        default='../dcmqi-1.2.4-mac/bin/itkimage2segimage',
                        help='Path to the DCMQI Pixelmed')
    opt = parser.parse_args()

    return opt


studycorr = {'preop':'Preop','intraop':'Intraop'}

def create_dicom_seg(path_nrrd, path_output, dcmqi_path):
    """
    Convert a SEG nrrd file to a dicom file with DCMqi
    """
    
    # Get SEG information
    structure = os.path.basename(path_nrrd).split('-')[3] # Type of structure
    ref_scan = os.path.basename(path_nrrd).split('-')[5].replace('.nrrd','') # Reference image
    
    patient_id = path_nrrd.split("/")[-3][4:]
    patient_name = 'CASE^'+patient_id
    study_id = studycorr[os.path.basename(path_nrrd).split('-')[1]]
    date = '19990101'
    
    # Get reference image path
    path_ref_study = os.path.join(path_output,f'{patient_id}-{patient_name}', f'{date}-{study_id}')
    ref_folder = [k for k in os.listdir(path_ref_study) if '-' in k and ref_scan==k.split('-')[1]]
    assert len(ref_folder)==1, f'Error {len(ref_folder)}, {ref_scan}, {os.path.basename(path_nrrd),  os.listdir(path_ref_study)}'
    path_ref_folder = os.path.join(path_ref_study, ref_folder[0])
    
    # Load json file
    f = open(f'json/{structure}.json')
    data = json.load(f)
    data['SeriesDescription'] = f'{structure} seg - MR ref: {ref_scan}'
    with open('temp.json', 'w') as f:
        json.dump(data, f)
    
    # Create output folder  
    os.makedirs(os.path.join(path_output,f'{patient_id}-{patient_name}', 'Annotations'), exist_ok=True)
    
    # create the command
    cmd = [dcmqi_path, 
           '--inputImageList', path_nrrd,
           '--inputDICOMDirectory', path_ref_folder,
           '--outputDICOM', os.path.join(path_output,f'{patient_id}-{patient_name}', 'Annotations', os.path.basename(path_nrrd).replace('.nrrd','.dcm')),
           '--inputMetadata', 'temp.json',
        ]
    # execute it
    subprocess.call(cmd)
    
    os.remove('temp.json')


def main():
    opt = parsing_data()
    cases = natsorted([k for k in os.listdir(opt.path_nrrd) if os.path.isdir(os.path.join(opt.path_nrrd, k))])
    for case in tqdm(cases):
        for folder in ['Annotations']:
            path_folder_case_session = os.path.join(opt.path_nrrd, case, folder)
            imgs =  [k for k in os.listdir(path_folder_case_session) if '.nrrd' in k]
            for img in imgs:
                create_dicom_seg(
                    os.path.join(path_folder_case_session, img),
                    opt.path_dicom,
                    opt.img2seg)

        
if __name__ == '__main__':
    main()
        
    
    

            
            
        