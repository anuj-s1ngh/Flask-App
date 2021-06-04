from PIL import Image
import datetime
import os


def resize_image(image, height, width):
    output_size = (height, width)
    img = Image.open(image)
    img.resize(output_size)
    # img.thumbnail(output_size)
    return img


# UTC_datetime = datetime.datetime.utcnow()
# UTC_datetime_timestamp = float(UTC_datetime.strftime("%s"))
# local_datetime_converted = datetime.datetime.fromtimestamp(UTC_datetime_timestamp)

if __name__ == '__main__':
    print(os.environ.get('SQLALCHEMY_DATABASE_URI'))
    pass
    # img = resize_image("C:/Users/anujs/PycharmProjects/FlaskApp/flaskapp/static/MEDIA/IMG/PROFILE_IMG/default.jpg", 125, 125)
    # img.save("C:/Users/anujs/PycharmProjects/FlaskApp/flaskapp/static/MEDIA/IMG/PROFILE_IMG/2.jpg")
