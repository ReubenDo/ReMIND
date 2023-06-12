# ReMIND
Scripts used for the conversion of the NRRD data to DICOM data



## Conversion of NRRD images to DICOM images

### Requirements
1. Java: can be downloaded from [here](https://www.oracle.com/java/technologies/downloads/)
2. 3D Slicer: can be downloaded from [here](https://download.slicer.org/)

### Command
To process images:

On MacOS:

```/Applications/Slicer.app/Contents/MacOS/Slicer  --no-splash --python-script conversion_imaging.py --path_nrrd [PATH_TCIA_NRRD] --path_dicom ./dicom ```

On Windows:

```Slicer.exe  --no-splash --python-script conversion_imaging.py --path_nrrd [PATH_TCIA_NRRD] --path_dicom ./dicom ```

## Conversion of NRRD SEG to DICOM SEG
### Requirements
1. DCMQI: binaries for your operating system are available [here](https://qiicr.gitbook.io/dcmqi-guide/opening/installation/binary_packages)

### Command
To process segmentations:

```python conversion_seg.py --path_nrrd [PATH_TCIA_NRRD] --path_dicom ./dicom --img2seg ../dcmqi-1.2.4-mac/bin/itkimage2segimage```



### Loading the DICOM files in 3D Slicer:
Drop a case folder, load the images and enjoy!
![image](https://github.com/ReubenDo/ReMIND/assets/17268715/8b057d4c-ab50-4884-b509-a615b7206c1c)

