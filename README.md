# ReMIND Data Conversion Scripts

This repository includes scripts designed for the conversion of ReMIND data between NRRD and DICOM formats. The scripts serve two primary purposes:

1. **Conversion from NRRD to DICOM for TCIA:**
    - Step 1: Conversion of NRRD images to DICOM images for ultrasound and MR data.
    - Step 2: Conversion of NRRD SEG to DICOM SEG for segmentation files.

2. **Conversion of TCIA Imaging Data from DICOM to NRRD:**
    - Convert DICOM imaging data downloaded from TCIA into NIfTI or NRRD formats.

## Example Output
Below is an example of a DICOM folder loaded in 3D Slicer:
![image](https://github.com/ReubenDo/ReMIND/assets/17268715/8b057d4c-ab50-4884-b509-a615b7206c1c)

## Conversion from NRRD to DICOM for TCIA
### Step 1: Conversion of NRRD images to DICOM images
- Ultrasound images are converted using the [Dicom3tools software](https://www.dclunie.com/dicom3tools.html) as multi-frame DICOM files.
- MR data is converted using [3D Slicer](https://download.slicer.org/).

#### Requirements
1. Java: Download from [here](https://www.oracle.com/java/technologies/downloads/)
2. 3D Slicer: Download from [here](https://download.slicer.org/)

#### Command
On MacOS:
```bash
/Applications/Slicer.app/Contents/MacOS/Slicer --no-splash --python-script conversion_imaging.py --path_nrrd [PATH_TCIA_NRRD] --path_dicom ./dicom
```

On Windows:
```bash
Slicer.exe  --no-splash --python-script nrrd_to_dicom_img.py --path_nrrd [PATH_TCIA_NRRD] --path_dicom ./dicom
```

### Step 2: Conversion of NRRD SEG to DICOM SEG
NRRD segmentation files are converted with dcmqi using DICOM images as a reference.

#### Requirements
1. dcmqi: binaries for your operating system are available [here](https://qiicr.gitbook.io/dcmqi-guide/opening/installation/binary_packages)

#### Command
To process segmentations:

```python nrrd_to_dicom_seg.py--path_nrrd [PATH_TCIA_NRRD] --path_dicom ./dicom --img2seg ../dcmqi-1.2.4-mac/bin/itkimage2segimage```

# Conversion of the imaging data from DICOM to NRRD
To convert DICOM imaging data downloaded from TCIA into NIfTI or NRRD formats, follow these guidelines:

#### Requirements
1. Download imaging data from [TCIA](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=157288106)
2. Python with the required packages (install with ```pip install -r requirements.txt```)

#### Command
To convert DICOM images into NIfTI format:
```python dicom_to_nifti-nrrd_img.py --path_dicom [PATH_REMIND_DATA] --nifti  ```

To convert DICOM images into NRRD format:
```python dicom_to_nifti-nrrd_img.py --path_dicom [PATH_REMIND_DATA] --nrrd  ```

Replace `[PATH_REMIND_DATA]` with the path to the downloaded ReMIND imaging data (e.g., `data/ReMIND_TCIA/manifest-1695134609823/ReMIND/`).


