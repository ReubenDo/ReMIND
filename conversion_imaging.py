import os
import subprocess
import slicer
import argparse
import DICOMScalarVolumePlugin

try:
    import pandas as pd 
except:
    slicer.util.pip_install('pandas')
    import pandas as pd 

try:
    from tqdm import tqdm
except:
    slicer.util.pip_install('tqdm')
    from tqdm import tqdm

import numpy as np

try:
    from natsort import natsorted
except:
    slicer.util.pip_install('natsort')
    from natsort import natsorted

try:
    import pydicom
except:
    slicer.util.pip_install('pydicom')
    import pydicom

errors  = []

def parsing_data():
    parser = argparse.ArgumentParser(
        description='Conversion NRRD images into DICOM')
    parser.add_argument('--path_nrrd',
                        type=str,
                        default='./nrrd',
                        help='Path to the input NRRD dataset')
    parser.add_argument('--path_dicom',
                        type=str,
                        default='./dicom_folder',
                        help='Path to the output DICOM dataset')
    opt = parser.parse_args()

    return opt


DATE = '19990101'

def download_pixelmed():
    from urllib.request import urlopen
    url = "http://www.dclunie.com/pixelmed/software/20221004_current/pixelmed.jar"
    data = urlopen(url).read()
    with open("pixelmed.jar", 'wb') as f:
        f.write(data)

# based on https://discourse.slicer.org/t/exporting-volumetric-ultrasound-to-dicom/22265/25?u=koeglfryderyk
def convert_nrrd_to_dicom_pure(path_nrrd, 
                               path_dicom,
                               patient_name='Patient Name',
                               patient_id='Patient ID',
                               study_id='Study ID', 
                               series_number='1', 
                               instance_number='1'):
    """
    Execute the conversion of a nrrd file to a dicom file with David's tool
    @param path_nrrd: path to the input nrrd file
    @param path_dicom: path to the output dicom file
    @param patient_name: Name of the patient
    @param patient_id: id of the patient
    @param study_id: id of the study
    @param series_number: number of the series (e.g. 1 for predura US)
    @param instance_number: instance number, often same as series number
    """

    # create the command
    path_jar = 'pixelmed.jar'
    if not os.path.isfile(path_jar):
        download_pixelmed()
    
    cmd = ['java', '-cp', path_jar, '-Djava.awt.headless=true', 'com.pixelmed.convert.NRRDToDicom',
           path_nrrd, path_dicom,
           patient_name, patient_id, study_id, series_number, instance_number]

    # execute it
    subprocess.call(cmd)


def add_info_to_dicom(path_dicom, study_instance_uid=None, study_description=None, series_description=None ,modality=None):
    """
    Add information to a dicom file
    @param path_dicom: path to the dicom file
    @param study_instance_uid: new study instance uid of the dicom file - needs to be the same for all files in the same study
    @param study_description: new study description of the dicom file so that it appears in 3D Slicer
    @param series_description: new series description of the dicom file so that it appears in 3D Slicer
    @param modality: new modality of the dicom file
    @return:
    """

    file = pydicom.dcmread(path_dicom)

    if study_instance_uid is not None:
        file.StudyInstanceUID = study_instance_uid

    if study_description is not None:
        file.StudyDescription = study_description

    if series_description is not None:
        file.SeriesDescription = series_description

    if modality is not None:
        file.Modality = modality
        
    file.StudyDate = DATE
        
    pydicom.dcmwrite(path_dicom, file)

def convert_dicom(path_nrrd, path_output, series_number, study_instanceid):
    """
    Convert a nrrd file to a dicom file with 3D Slicer
    @param path_nrrd: path to the NRRD file
    @param path_output: path to the root DICOM folder
    @param series_number: number of the series during DICOM conversion (e.g. 1 for iUS pre-dura)
    @param study_instanceid: id of the study
    """
    
    patient_id = path_nrrd.split("/")[-3][4:]
    patient_name = 'CASE^'+patient_id
    study_id = path_nrrd.split("/")[-2].split("-")[0]
    

    series_description = path_nrrd.replace('-r.n','.n').split('-')[-1].replace('.nrrd','')

    study_instance_uid = '1' if "Preop" in path_nrrd else '2'
    study_instance_uid += '.' + patient_id
    modality = "MR" if "MR" in path_nrrd else "US"
    # modality = "MR"

    if "US" in path_nrrd:
        if 'pre_dura' in path_nrrd:
            series_number = '1'
        elif 'post_dura' in path_nrrd:
            series_number = '2'
        elif 'pre_imri' in path_nrrd:
            series_number = '3'
        else:
            raise Exception(f'US without being in (pre_dura, post_dura, pre_imri) {path_nrrd}')
        series_description= f'US_{series_description}'

    volumeNode = slicer.util.loadVolume(path_nrrd)
    # Create patient and study and put the volume under the study
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    # set IDs. Note: these IDs are not specifying DICOM tags, but only the names that appear in the hierarchy tree
    patientItemID = shNode.CreateSubjectItem(shNode.GetSceneItemID(), patient_id)
    studyItemID = shNode.CreateStudyItem(patientItemID, study_id)
    volumeShItemID = shNode.GetItemByDataNode(volumeNode)
    shNode.SetItemParent(volumeShItemID, studyItemID)
    exporter = DICOMScalarVolumePlugin.DICOMScalarVolumePluginClass()
    exportables = exporter.examineForExport(volumeShItemID)
    renames = []
    for exp in exportables:
        # set output folder
        exp.directory = os.path.join(path_output,f'{patient_id}-{patient_name}', f'{DATE}-{study_id}')
        # here we set DICOM PatientID and StudyID tags
        exp.setTag('PatientID', patient_id)
        exp.setTag('StudyID', study_id)
        exp.setTag('Modality', modality)
        exp.setTag('StudyDescription', study_id)
        exp.setTag('SeriesDescription', series_description)
        exp.setTag('SeriesNumber', series_number)
        exp.setTag('PatientName', patient_name)
        exp.setTag('StudyDate', DATE)
        exp.setTag('StudyInstanceUID', study_instanceid)
        renames.append((f'ScalarVolume_{exp.subjectHierarchyItemID}', f'{series_number}-{series_description}'))

    exporter.export(exportables)
    slicer.mrmlScene.RemoveNode(volumeNode)
    slicer.mrmlScene.Clear(0)
    
    for old,new in renames: 
        path_final = os.path.join(path_output,f'{patient_id}-{patient_name}', f'{DATE}-{study_id}', new)
        os.rename(
            os.path.join(path_output,f'{patient_id}-{patient_name}', f'{DATE}-{study_id}', old),
            path_final)
    
        dcms = [os.path.join(path_final, k) for k in os.listdir(path_final) if 'dcm' in k]
        try:
          for dcm in dcms:
              file = pydicom.dcmread(dcm, force=True)
              file.ScanningSequence = 'RM'
              file.SequenceVariant = 'NONE'
              file.MRAcquisitionType = ''
              file.ScanOptions = ''
              file.RepetitionTime = ''
              file.EchoTime = ''
              file.EchoTrainLength = ''
              file.Laterality = ''
              file.DeidentificationMethod = 'PyDeface-NiftyReg'
              obs = file.RescaleType
              del obs
              pydicom.dcmwrite(dcm, file)
        except Exception as e:
          errors.append((e,path_final))
      

def convert_dicom_clunie(path_nrrd, path_output, series_number, study_instanceid):
    """
    Convert a nrrd file to a dicom file with David's tool
    @param path_nrrd: path to the NRRD file
    @param path_output: path to the root DICOM folder
    @param series_number: number of the series during DICOM conversion (e.g. 1 for iUS pre-dura)
    @param study_instanceid: id of the study
    """
    # Get information
    patient_id = path_nrrd.split("/")[-3][4:]
    patient_name = 'CASE^'+patient_id
    study_id = path_nrrd.split("/")[-2].split("-")[0]

    series_description = path_nrrd.replace('-r.n','.n').split('-')[-1].replace('.nrrd','')

    study_instance_uid = '1' if "Preop" in path_nrrd else '2'
    study_instance_uid += '.' + patient_id
    modality = "MR" if "MR" in path_nrrd else "US"
    
    if "US" in path_nrrd:
        if 'pre_dura' in path_nrrd:
            series_number = '1'
        elif 'post_dura' in path_nrrd:
            series_number = '2'
        elif 'pre_imri' in path_nrrd:
            series_number = '3'
        else:
            raise Exception(f'US without being in (pre_dura, post_dura, pre_imri) {path_nrrd}')
        series_description= f'US_{series_description}'
    
    path_dicom = os.path.join(path_output,f'{patient_id}-{patient_name}', f'{DATE}-{study_id}', f'{series_number}-{series_description}')
    os.makedirs(path_dicom, exist_ok=True)
    path_dicom = os.path.join(path_dicom, f'{series_description}.dcm')

    # first do the standard conversion
    convert_nrrd_to_dicom_pure(path_nrrd, path_dicom,
                               patient_name=patient_name, patient_id=patient_id,
                               study_id=study_id, series_number=series_number, instance_number=series_number)

    # then add the missing info
    add_info_to_dicom(path_dicom, study_instance_uid=study_instanceid, study_description=study_id,
                      series_description=series_description, modality=modality)


def main():
    opt = parsing_data()
    cases = natsorted([k for k in os.listdir(opt.path_nrrd) if os.path.isdir(os.path.join(opt.path_nrrd,k))])
    problems = []
    df = {'case':[],'preop':[],'intraop':[]}
    for case in tqdm(cases):
        # Start with pre-operative MRI
        folder = 'Preop-MR'
        path_folder_case_session = os.path.join(opt.path_nrrd,case,folder)
        imgs =  natsorted([k for k in os.listdir(path_folder_case_session) if '.nrrd' in k])
        study_instanceid_preop = f'1.3.6.1.4.1.5962.99.1.3781888186.{np.random.randint(10**9)}.{np.random.randint(10**6)}.4.0'
        for i,img in enumerate(imgs):
            convert_dicom(
                path_nrrd=os.path.join(path_folder_case_session,img),
                path_output=opt.path_dicom,
                series_number=str(i+1),
                study_instanceid=study_instanceid_preop
                )
        
        # Then, intra-operative US
        study_instanceid_intraop = f'1.3.6.1.4.1.5962.99.1.3781888186.{np.random.randint(10**9)}.{np.random.randint(10**6)}.4.0'
        folder = 'Intraop-US'
        path_folder_case_session = os.path.join(opt.path_nrrd,case,folder)
        imgs = natsorted([k for k in os.listdir(path_folder_case_session) if 'nrrd' in k])
        for i,img in enumerate(imgs):
            convert_dicom_clunie(
                path_nrrd=os.path.join(path_folder_case_session,img),
                path_output=opt.path_dicom,
                series_number=str(i+1),
                study_instanceid=study_instanceid_intraop,
                )

        # Finally, intra-operative MR
        folder = 'Intraop-MR'
        path_folder_case_session = os.path.join(opt.path_nrrd,case,folder)
        imgs =  natsorted([k for k in os.listdir(path_folder_case_session) if '.nrrd' in k])
        for i,img in enumerate(imgs):
            convert_dicom(
                path_nrrd=os.path.join(path_folder_case_session,img),
                path_output=opt.path_dicom,
                series_number=str(i+4), 
                study_instanceid=study_instanceid_intraop)
            
        df['case'].append(case)
        df['preop'].append(study_instanceid_preop)
        df['intraop'].append(study_instanceid_intraop)
 
    df = pd.DataFrame(df)
    df.to_csv('corr.csv')
    print('----------- errors -------------')
    print(errors)
    
    exit()

if __name__ == '__main__':
    main()

            
            
        