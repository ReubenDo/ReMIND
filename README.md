# ReMIND Scripts
These repository contains the scripts used to convert the ReMIND NRRD data into DICOM data.

Here is an example of an output DICOM folder loaded in 3D Slicer:
![image](https://github.com/ReubenDo/ReMIND/assets/17268715/8b057d4c-ab50-4884-b509-a615b7206c1c)

## Step 1: Conversion of NRRD images to DICOM images
The ultrasound images are converted using the [Dicom3tools software](https://www.dclunie.com/dicom3tools.html) as multi-frame DICOM files.

The MR data is converted using [3D Slicer](https://download.slicer.org/).

### Requirements
1. Java: can be downloaded from [here](https://www.oracle.com/java/technologies/downloads/)
2. 3D Slicer: can be downloaded from [here](https://download.slicer.org/)

### Command
To process images:

On MacOS:

```/Applications/Slicer.app/Contents/MacOS/Slicer  --no-splash --python-script conversion_imaging.py --path_nrrd [PATH_TCIA_NRRD] --path_dicom ./dicom ```

On Windows:

```Slicer.exe  --no-splash --python-script conversion_imaging.py --path_nrrd [PATH_TCIA_NRRD] --path_dicom ./dicom ```

## Step 2: Conversion of NRRD SEG to DICOM SEG
The NRRD segmentation files are converted with dcmqi using the DICOM images as reference.

### Requirements
1. dcmqi: binaries for your operating system are available [here](https://qiicr.gitbook.io/dcmqi-guide/opening/installation/binary_packages)

### Command
To process segmentations:

```python conversion_seg.py --path_nrrd [PATH_TCIA_NRRD] --path_dicom ./dicom --img2seg ../dcmqi-1.2.4-mac/bin/itkimage2segimage```

