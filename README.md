# Face Recognition

Face recognition using python and mysql.

*******

## Useage

### Environment

Create virtual environment using Anaconda.

```shell
conda create -n face python=3.x
conda activate face
pip install -r requirements.txt
```


## Run

### 1. Face Recognition

#### 1.1 Collect Face Data

In `face_capature.py`

```python
user_name = "Jack"   # the name
NUM_IMGS = 400       # the number of saved images
```

In command line

```shell
python3 face_capture.py
```
The camera will be activated and the captured images will be stored in `data/Jack` folder.      
**Note:** Only one person’s images can be captured at a time.

#### 1.2 Train a Face Recognition Model
```shell
python3 train.py
```
`train.yml` and `labels.pickle` will be created at the current folder.



### 2. Database

![ER-diagram](img/ER-diagram.png)

#### import from sql file

```mysql
mysql> source facerecognition.sql
mysql> source sampleData.sql
```


### 3. Login Interface
**NOTE:** The password of `root@localhost` should be stored in a `.password` under current directory.

```shell
python3 faces_gui.py
```

The camera will be activated and recognize your face using the pretrained model.    
