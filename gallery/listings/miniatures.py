def miniature(path_image):
    # resize and crop photo given by its path in format 500x400
    # returns the resized and cropped photo
    from PIL import Image
    import os

    with Image.open(path_image) as im:
        w = im.width
        h = im.height

        #calcul rapport de réduction en W et en H
        r_w = w/500
        r_h = h/400
        if r_w > r_h:
            r_size = (int(w//r_h), 400)
                # calcul du tuple pour le crop
            l_c = int( (r_size[0] - 500)//2) # left corner
            u = 0   # upper
            r_c = 500 + l_c  # Right corner
            l =  400 #lower
        else:
            r_size = (500, int(h // r_w) )
                # calcul du tuple pour le crop
            l_c = 0                            # left corner
            u = int( (r_size[1] - 400)//2  )   # upper
            r_c = 500                          # Right corner
            l =  400 + u                       #lower

        try:
            im_resized = im.resize( r_size )
        except:
            print("problem resizing photo")
            with open ('log_err.log','a') as log:
                log.write(path_image + '          exception in image.resize()\n')
            return None

        try:
            orientation = im._getexif()[0x112]
            if orientation == 6:
                im_resized =im_resized.rotate(-90)
            elif orientation == 8:
                im_resized =im_resized.rotate(90)
            elif orientation == 3:
                im_resized =im_resized.rotate(180)
        except :
            print("problème dans les données EXIF")

        try:
            im_crop = im_resized.crop( (l_c,  u, r_c, l)   )
        except:
            print("problem cropping photo")
            with open ('log_err.log','a') as log:
                log.write(path_image + '          exception in image.crop()\n')
            return None
    return im_crop

