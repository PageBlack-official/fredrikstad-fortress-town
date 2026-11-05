# 01_bygg_finnes: FEIL

krasjet: laude/fredrikstad-fortress-town/regler/01_bygg_finnes.py", line 6, in <module>
    b = data('bygg'); im, px = flyfoto(); H, W = im.shape[:2]; hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
                                                 ^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'shape'
