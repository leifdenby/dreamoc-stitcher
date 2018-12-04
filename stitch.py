# coding: utf-8
"""
Utility to stich three images together to make an image which could be rendered
on the Dreamoc

Leif Denby 4/12/2018, GPL3 License
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
from scipy.constants import pi
from scipy.misc import imread
import numpy as np
import imageio


class DreamocImageSticher():
    def __init__(self, w=1920, h=1080, dpi=200):
        self.w = w
        self.h = h
        self.dpi = dpi

        assert w > h

        # calculate centers of zones L, C, R (left, center, right)
        i_c_C = w//2
        j_c_C = w//4
        self.centers = [
            ('L', (w/4, w/2), -pi/2),
            ('C', (i_c_C, j_c_C), 0.),
            ('R', (3.*w/4, w/2), pi/2),
        ]

        self.i_c_C = i_c_C
        self.j_c_C = j_c_C

        # to insert image at right place need to transpose, clip and do a asked insert into final image
        i, j = np.arange(w), np.arange(h)
        i_, j_ = np.meshgrid(i, j, indexing='ij')
        self.mask_L = np.logical_and(j_ > i_, i_ < w/2)
        self.mask_R = np.logical_and(j_ > (w - i_), i_ > w/2)
        self.mask_C = np.logical_and(
            np.logical_not(self.mask_L), np.logical_not(self.mask_R)
        )

    def make_screen_fig(self):
        w, h, dpi = self.w, self.h, self.dpi
        
        return plt.subplots(figsize=(w/dpi, h/dpi))

    def plot_screen(self, ax=None, color='black'):
        w, h = self.w, self.h
        if ax is None:
            fig, ax = self.make_screen_fig()

        screen_patch = patches.Rectangle((0, 0), w, h, linewidth=1, 
                facecolor='none', edgecolor=color, linestyle='--')

        # the seperating line appears to be at 45 deg to x-axis, and so separating line must end at h=w/2
        sep_left = mlines.Line2D((0, w/2), (0, w/2), linewidth=1, linestyle=':', color=color)
        sep_right = mlines.Line2D((w, w/2), (0, w/2), linewidth=1, linestyle=':', color=color)
        sep_center = mlines.Line2D((w/2, w/2), (w/2, h), linewidth=1, linestyle=':', color=color)

        for name, pt, rot in self.centers:
            #plt.plot(pt[0], pt[1], marker='x')
            plt.text(pt[0], pt[1], name, rotation=rot*180./pi, color=color)
            #plt.text(100, 100, name, fontsize=0.1)

        ax.add_patch(screen_patch)
        ax.add_line(sep_left)
        ax.add_line(sep_right)
        ax.add_line(sep_center)

        ax.set_xlim(-0.1*w, 1.1*w)
        ax.set_ylim(-0.1*h, 1.1*h)

        return ax

    def plot_img(self, img, **kwargs):
        plt.imshow(np.transpose(img, axes=(1,0,2)), **kwargs)

    def _center_image(self, img):
        w, h = self.w, self.h
        w_in, h_in, n_colors = img.shape
        i_c_C, j_c_C = self.i_c_C, self.j_c_C

        # ensure we have a minimum an image the size of the output
        w_min, h_min = max(w_in, w), max(h_in, h)
        img_ = np.ones((w_min, h_min, n_colors)).astype(img.dtype)
        img_[:w_in, :h_in] = img

        # center on 0,0
        img_ = np.roll(np.roll(img_, -w_in//2, axis=0), -h_in//2, axis=1)

        # center on the C's center
        img_ = np.roll(np.roll(img_, i_c_C, axis=0), j_c_C, axis=1)

        # crop to the final image's extent
        img_ = img_[:w,:h]

        return img_


    def place_central_image(self, img, img_output):
        mask_C = self.mask_C

        img_ = self._center_image(img)
        img_output[mask_C] = img_[mask_C]
        
        return img_output


    def place_left_img(self, img, img_output):
        h, mask_L = self.h, self.mask_L
        img_ = self._center_image(img)
        img_ = np.rot90(img_, axes=(1,0), k=1)[:,:h]

        # need to crop the mask before we apply it
        m = mask_L[:h]
        img_output[:h][m] = img_[m]

        return img_output


    def place_right_img(self, img, img_output):
        w, h, mask_R = self.w, self.h, self.mask_R

        img_ = self._center_image(img)

        img_ = np.rot90(img_, axes=(1,0), k=-1)
        w_ = img_.shape[0]

        img_temp = np.zeros_like(img_output)
        img_temp[:w_] = img_[:w_,:h]
        img_temp = np.roll(img_temp, axis=0, shift=w-w_)

        img_output[mask_R] = img_temp[mask_R]

        return img_output

    def _read_img(self, fn):
        return np.transpose(imageio.imread(fn), axes=(1,0,2))

    def __call__(self, fn_img_L, fn_img_R, fn_img_C):
        img_L = self._read_img(fn_img_L)
        img_R = self._read_img(fn_img_R)
        img_C = self._read_img(fn_img_C)

        w, h = self.w, self.h
        n_colors = img_L.shape[-1]
        assert img_L.shape[-1] == img_R.shape[-1] == img_C.shape[-1]

        img_output = 255*np.ones((w, h, n_colors)).astype(img_L.dtype)
        img_output = self.place_left_img(img_L, img_output)
        img_output = self.place_central_image(img_C, img_output)
        img_output = self.place_right_img(img_R, img_output)

        return img_output


if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('img_L', help='left image filename')
    argparser.add_argument('img_C', help='center image filename')
    argparser.add_argument('img_R', help='right image filename')
    argparser.add_argument('--width', help='width', default=1920, type=int)
    argparser.add_argument('--height', help='height', default=1080, type=int)
    argparser.add_argument('--dpi', help='dpi', default=200, type=int)
    argparser.add_argument('--out', help='output filename', default='combined.png')

    args = argparser.parse_args()

    stitcher = DreamocImageSticher(w=args.width, h=args.height, dpi=args.dpi)
    img_output = stitcher(fn_img_L=args.img_L, fn_img_C=args.img_C,
                          fn_img_R=args.img_R)

    imageio.imwrite(args.out, np.rot90(img_output, k=1))
    print("Wrote combined image to {}".format(args.out))
