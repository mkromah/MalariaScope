"""One shared input pipeline for model training, evaluation, and web inference.

ImageOps.pad scales to fit a 224x224 square without changing the original
aspect ratio, then pads with a black border (consistent with the crop
backgrounds in the NIH cell-image dataset).

Apply image augmentations to TRAINING images only.
"""
from PIL import Image, ImageOps
from torchvision import transforms

IMAGE_SIZE = (224, 224)
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)


def resize_with_padding(image: Image.Image) -> Image.Image:
    """Fit a blood-cell image in a 224x224 square; keep its proportions."""
    return ImageOps.pad(
        image.convert("RGB"),
        IMAGE_SIZE,
        method=Image.Resampling.BILINEAR,
        color=(0, 0, 0),
        centering=(0.5, 0.5),
    )


def image_transform(augment: bool = False) -> transforms.Compose:
    """Return the identical image preprocessing for all project components."""
    operations = [transforms.Lambda(resize_with_padding)]
    if augment:
        operations.extend([
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
        ])
    operations.extend([
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
    return transforms.Compose(operations)
