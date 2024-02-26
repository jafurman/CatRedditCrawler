import pymongo
import traceback


def connectDataBase():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        # database connection is localhost client.[databaseName]
        datab = client.CatDB
        return datab
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully.. rawr")


def saveTaggedImages(db, tagged_images):
    try:
        # Create a new collection in the database
        col = db.TaggedSRImages

        # Insert the tagged_images data into the collection
        col.insert_many(tagged_images)

        print("Tagged images saved successfully!")

    except Exception as error:
        print("Mongo DB Error")
        traceback.print_exc()


def extractUniqueImagesAndPredictions(db):
    try:
        col = db.OrganizedCatWords
        cursor = col.find({}, {'display_name': 1, 'UniqueImagesAndPredictions': 1})

        tagged_images = []

        for document in cursor:
            display_name = document.get('display_name')
            unique_images_and_predictions = document.get('UniqueImagesAndPredictions')

            if 'UniqueImagesAndPredictions' in document and unique_images_and_predictions:
                for entry in unique_images_and_predictions:
                    entry_data = structureEntry(entry)
                    tagged_images.append({**entry_data, 'display_name': display_name})

        return tagged_images

    except Exception as error:
        print("Mongo DB Error")
        traceback.print_exc()


def structureEntry(entry):
    structured_data = {}
    image_file = entry.get('Image_File')
    predictions = entry.get('Predictions', [])
    if image_file:
        prediction_list = {prediction.get('Prediction'): prediction.get('Likelihood') for prediction in predictions}
        structured_data[image_file] = prediction_list
    return structured_data


db = connectDataBase()

# Call the function to extract data from OrganizedCatWords collection
tagged_images_data = extractUniqueImagesAndPredictions(db)

# Call the function to save tagged images to TaggedSRImages collection
saveTaggedImages(db, tagged_images_data)
