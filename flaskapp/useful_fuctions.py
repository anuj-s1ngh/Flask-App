from PIL import Image
import datetime
import os
import random
import string
import secrets


def random_string():
    num = 16  # define the length of the string
    # define the secrets.choice() method and pass the string.ascii_letters + string.digits as an parameters.
    res = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(num))
    # Print the Secure string with the combonation of letters, digits and punctuation
    # print("Secure random string is :" + str(res))
    return str(res)


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
    random_string()

    # print(os.environ.get('SQLALCHEMY_DATABASE_URI'))
    # pass
    # img = resize_image("C:/Users/anujs/PycharmProjects/FlaskApp/flaskapp/static/MEDIA/IMG/PROFILE_IMG/default.jpg", 125, 125)
    # img.save("C:/Users/anujs/PycharmProjects/FlaskApp/flaskapp/static/MEDIA/IMG/PROFILE_IMG/2.jpg")
