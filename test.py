import imageio

# Make sure you have imageio-ffmpeg installed:
# pip install imageio imageio-ffmpeg

reader = imageio.get_reader('input.webm',  'ffmpeg')
meta   = reader.get_meta_data()
fps    = meta['fps']  # frames per second of the source

# Create an animated WebP writer; duration is seconds per frame
writer = imageio.get_writer(
    'output.webp',
    format='webp',
    mode='I',            # “I” = multiple images (animation)
    duration=1/fps       # pause between frames
)

for frame in reader:
    writer.append_data(frame)

writer.close()
reader.close()
