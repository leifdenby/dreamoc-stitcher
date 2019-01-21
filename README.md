# Dreamoc image stitcher

This utility facilitates stitching three images together (the intention is
these will be the left, center and right-side view of a scene) together to form
a single image to be shown on the Dreamoc.

## Installation and usage

Install requirements with pip

> pip install -r requirements.txt

Run

> python stitch.py img_L.png img_C.png img_R.png

## Examples


### Mobius strip

**input**

<table>
<tr>
<td><img src='examples/mobius_L.png' width=200 /></td>
<td><img src='examples/mobius_C.png' width=200 /></td>
<td><img src='examples/mobius_R.png' width=200 /></td>
</tr>
</table>

**output**

<img src='examples/mobius_combined.png' width=200 />


### Text strip

**input**

<table>
<tr>
<td><img src='examples/text_LEFT.png' width=200 /></td>
<td><img src='examples/text_CENTER.png' width=200 /></td>
<td><img src='examples/text_RIGHT.png' width=200 /></td>
</tr>
</table>

**output**

<img src='examples/text_combined.png' width=200 />
