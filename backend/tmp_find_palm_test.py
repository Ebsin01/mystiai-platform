import sys
sys.path.insert(0, '.')
from app.services.pdf_service import find_palm_image
class R: pass
r = R()
# try with basename only
r.analysis = type('A', (), {'image_filename':'20f3b986-585a-46fd-9dac-f0a097e20209_002_F_L_38.JPG'})()
print('RESULT:', find_palm_image(r))
# try with plain basename that likely doesn't exist exactly
r.analysis = type('A', (), {'image_filename':'002_F_L_38.JPG'})()
print('RESULT2:', find_palm_image(r))
# try with uploads/palms prefixed
r.analysis = type('A', (), {'image_filename':'uploads/palms/20f3b986-585a-46fd-9dac-f0a097e20209_002_F_L_38.JPG'})()
print('RESULT3:', find_palm_image(r))
