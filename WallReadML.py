# Importing the Keras libraries and packages
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
from keras.preprocessing import image
from keras.models import load_model
from keras import backend as K
import os
def train_conditional(working_dir='./stored_backgrounds'):
    import pickle
    # Part 2 - Fitting the CNN to the images
    train_dir = str(working_dir)
    # test_dir = './stored_backgrounds/Prediction/test'
    if not os.path.isdir(train_dir + '/Like'):
        os.makedirs(str(train_dir + '/Dislike'))
        os.makedirs(str(train_dir + '/Like'))
        # os.makedirs(test_dir + '/Dislike_test')
        # os.makedirs(test_dir + '/Like_test')
    trainSize = sum([len(files) for r, d, files in os.walk(train_dir + '/Like')] + [len(files) for r, d, files in os.walk(train_dir + '/Dislike')])
    lik = sum([len(files) for r, d, files in os.walk(train_dir + '/Like')])
    dis = sum([len(files) for r, d, files in os.walk(train_dir + '/Dislike')])
    print('Like size:',lik , 'Dislike size:',dis)
    # testSize = sum([len(files) for r, d, files in os.walk(test_dir)])
    

    skipTrain = False
    if lik <= 1 or dis <= 1:
        skipTrain = True
    if trainSize > 2 and not skipTrain:
        if os.path.isfile(str(train_dir + '/reccomender.wal')) and os.path.isfile(str(train_dir + '/reccomend_engine.wal')):
            reccomender = pickle.load(open(str(train_dir + '/reccomender.wal'),'rb'))
            classifier = load_model(str(train_dir + 'reccomend_engine.wal'))
            training_set = None
            # print('Current Test Size:',testSize,' Past Test Size:',reccomender['testSize'])
            print('Current Train Size:',trainSize,' Past Train Size:',reccomender['trainSize'])
            if (trainSize is reccomender['trainSize']):
                skipTrain = True
        if not skipTrain:
            # Initialising the CNN
            classifier = Sequential()
            # Step 1 - Convolution
            classifier.add(Conv2D(64, (3, 3), input_shape = (64, 64, 3), activation = 'relu'))
            # Step 2 - Pooling
            classifier.add(MaxPooling2D(pool_size = (2, 2)))
            # Adding a second convolutional layer
            classifier.add(Conv2D(32, (3, 3), activation = 'relu'))
            classifier.add(MaxPooling2D(pool_size = (2, 2)))
            # Step 3 - Flattening
            classifier.add(Flatten())
            # Step 4 - Full connection
            classifier.add(Dense(units = 256, activation = 'relu'))
            classifier.add(Dense(units = 128, activation = 'relu'))
            classifier.add(Dense(units = 64, activation = 'relu'))
            classifier.add(Dense(units = 1, activation = 'sigmoid'))
            # Compiling the CNN
            classifier.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])
            train_datagen = ImageDataGenerator(rescale = 1./255, shear_range = 0.2, zoom_range = 0.2, horizontal_flip = True, validation_split=0.25)
            # test_datagen = ImageDataGenerator(rescale = 1./255, shear_range = 0.2, zoom_range = 0.2, horizontal_flip = True)
            training_set = train_datagen.flow_from_directory(train_dir, target_size = (64, 64), batch_size = 32, class_mode = 'binary', seed=12)
            # test_set = test_datagen.flow_from_directory(test_dir, target_size = (64, 64), batch_size = 32, class_mode = 'binary')
            classifier.fit_generator(training_set, steps_per_epoch = 10, epochs = 2, validation_steps = 10)
            # Part 3 - Making new predictions
            recommender = {
                'trainSize':trainSize,
                # 'testSize':testSize,
                'classifier':None,
            }
            classifier.save(str(train_dir + '/reccomend_engine.wal'))
            out = open(str(train_dir + '/reccomender.wal'),'wb')
            pickle.dump(recommender, out)
            out.close()
        return classifier, training_set
    else:
        return None, None

def predict_LD(wal_address,classifier=None,training_set=None,working_dir='./stored_backgrounds'):
    print('Evaluating:', wal_address)
    evaluations = ("Evaluating: " + wal_address)
    test_image = image.load_img(wal_address, target_size = (64, 64))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis = 0)
    
    if not classifier:
        classifier, training_set = train_conditional(working_dir=working_dir)
    if classifier is not None:
        result = classifier.predict(test_image)
    else:
        result = [[1]]
    K.clear_session()
    # training_set.class_indices
    if result[0][0] == 1:
        prediction = 'Like'
    else:
        prediction = 'Dislike'
    
    print('Decision: ',prediction, ' | Certainty:', str(result[0][0]*100) + '%' )
    return([prediction, evaluations])

def files(root):  
    for path, subdirs, files in os.walk(root):
        for name in files:
            yield os.path.join(path, name)

if __name__ == "__main__":
    results = {
        'Like':[],
        'Dislike':[]
    }
    classifier, training_set = train_conditional()

    for fil in files('./stored_backgrounds'):
        result_arr = predict_LD(fil, classifier, training_set)
        results[result_arr[0]].append(result_arr[1])

    for key in results.keys():
        print('--- ',key, ' ---')
        for item in results[key]:
            print(' ',item)