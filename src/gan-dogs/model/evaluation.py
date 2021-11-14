import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
import cv2

from .utils import scale_images, calculate_fid


def sample(gan, train_dataset):
    """Generate and visualize sample generated by the GAN

    Args:
        gan (GAN): Compiled GAN model
        train_dataset (tf.data.Dataset): training data to sample from
    """

    random_latent_vectors = tf.random.truncated_normal(
        shape=(1, gan.latent_dim)
    )
    random_labels = tf.math.floor(gan.num_classes * tf.random.uniform((1, 1)))

    inputs = (random_latent_vectors, random_labels)

    gen_imgs = gan(inputs, training=False)

    real_imgs, real_labels = next(iter(train_dataset))
    real_img = real_imgs[:1, ...]
    real_label = real_labels[:1, ...]

    pred_real = gan.discriminator(real_img, real_label, training=False)
    pred_gen = gan.discriminator(gen_imgs, random_labels, training=False)

    print("Probability of real image being real:", tf.nn.sigmoid(pred_real))
    print("Probability of generated image being real:", tf.nn.sigmoid(pred_gen))

    img = gen_imgs[0]
    img = (img + 1.) / 2.
    if (img.shape[-1] == 1):
        img = np.squeeze(img, axis=-1)
        plt.title("Generated image")
        plt.imshow(img, cmap='gray')
    else:
        plt.title("Generated image")
        plt.imshow(img)
    plt.show()


def loss_curve(history):
    """Visualize the training loss curve.

    Args:
        history (tf.keras.callbacks.History): training history
    """
    plt.plot(history.history['g_loss'], label='generator loss')
    plt.plot(history.history['d_loss'], label='discriminator loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')

    plt.grid(axis='y')
    plt.legend(loc='lower right')
    plt.show()


def compute_fid(gan, real_images):
    """Compute FID score to evaluate GAN model performance

    Args:
        gan (GAN): GAN model
        real_images (tf.Tensor): real images from training dataset

    Returns:
        int: computed FID score
    """

    # generate images
    num_images = real_images.shape[0]
    latent_samples = tf.random.truncated_normal(shape=(16, gan.latent_dim))
    random_labels = tf.math.floor(
        gan.num_classes * tf.random.uniform(shape=[16, 1]))
    inputs = (latent_samples, random_labels)

    generated_images = gan(inputs, training=False)

    # resize images
    images1 = scale_images(real_images, (299, 299, 3))
    images2 = scale_images(generated_images, (299, 299, 3))

    # calculate fid
    fid = calculate_fid(images1, images2)
    return fid


def plot_imgs_grid(imgs, path=None):
    """Plot a grid of generated images

    Args:
        imgs (tf.Tensor): images to plot
        path (str, optional): path to directory where to save images. Defaults to None.
    """
    n_imgs = imgs.shape[0]
    grid_side = np.sqrt(n_imgs)

    fig, axes = plt.subplots(
        int(round(grid_side)),
        int(round(grid_side)),
        figsize=(n_imgs, n_imgs)
    )

    if path:
        file_counter = sum([len(files) for r, d, files in os.walk(path)])

    axes = np.reshape(axes, (-1,))
    for i, ax in enumerate(axes):
        img = imgs[i, ...]
        img = (img + 1.) / 2.
        if img.shape[-1] == 1:
            img = np.squeeze(img, axis=-1)
            ax.imshow(img, cmap='gray')
        else:
            ax.imshow(img)
        if path:
            # save images

            name = 'Dog_'+str(file_counter+i)
            image_path = os.path.join(path, name)

            img = 255 * img.numpy()
            img = img.astype('uint8')

            cv2.imwrite(image_path+'.jpg', img)
            print("Image saved as: "+name)

    plt.show()


def generate_and_plot_images(gan, num_images, save_path=None):
    """Generate and plot images from the trained GAN model.

    Args:
        gan (GAN): trained GAN model
        num_images (int): number of images to plot
        save_path (str, optional): path to directory where to save images. Defaults to None.
    """
    latent_samples = tf.random.truncated_normal(
        shape=(num_images, gan.latent_dim)
    )
    random_labels = tf.math.floor(
        gan.num_classes * tf.random.uniform(shape=[num_images, 1]))

    inputs = (latent_samples, random_labels)
    generated_images = gan(inputs, training=False)

    plot_imgs_grid(generated_images, path=save_path)
