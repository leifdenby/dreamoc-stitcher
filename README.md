# Dreamoc image stitcher

This utility facilitates stitching three images together (the intention is
these will be the left, center and right-side view of a scene) together form
a single image to be shown on the Dreamoc.

## Installation and usage

Install requirements with pip

> pip install -r requirements.txt

Run

> python stitch.py img_L.png img_C.png img_R.png

## Example


**input**

<table>
<tr>
<td><img src='example_L.png' width=200 /></td>
<td><img src='example_C.png' width=200 /></td>
<td><img src='example_R.png' width=200 /></td>
</tr>
</table>

**output**

<img src='combined.png' width=200 />
