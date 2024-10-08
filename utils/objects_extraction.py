import json
# For drawing onto the image.
import numpy as np
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

import tensorflow as tf

import matplotlib.pyplot as plt

def get_json_data(path):
    file = open(path)
    data = json.load(file)
    return data

def get_json_objs(json_data):
    boxes = np.array([[float(num) for num in box] for box in json_data["detection_boxes"]])
    class_names = json_data["detection_class_names"]
    scores = np.array([np.float32(i) for i in json_data["detection_scores"]])
    class_entities = json_data["detection_class_entities"]
    return boxes, class_names, scores, class_entities
    
def get_unique_json_objs_from_list(json_list, max_boxes=10, min_score=0.5):
    unique_objs = []
    for json_file in json_list:
        data = get_json_data(json_file)
        boxes, _, scores, class_entities = get_json_objs(json_data=data)
        
        for i in range(min(boxes.shape[0], max_boxes)):
            if scores[i] >= min_score:
                if class_entities[i] not in unique_objs:
                    unique_objs.append(class_entities[i])
    unique_objs_np = np.asarray(unique_objs)                
    return unique_objs_np

def retrieve_imgs_containing_obj(retrieval_json_list, obj_entity):
    results = []
    for json_file in retrieval_json_list:
        data = get_json_data(json_file)
        _, _, scores, class_entities = get_json_objs(json_data=data)
        if obj_entity in class_entities:
            results.append(json_file)
    return results


def display_image(image):
  fig = plt.figure(figsize=(20, 15))
  plt.grid(False)
  plt.imshow(image)

def load_img(path):
  img = tf.io.read_file(path)
  img = tf.image.decode_jpeg(img, channels=3)
  return img

def crop_bbox_on_image(image, ymin, xmin, ymax, xmax):
    im_width, im_height = image.size
    (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                            ymin * im_height, ymax * im_height)
    

def draw_bounding_box_on_image(image,
                               ymin,
                               xmin,
                               ymax,
                               xmax,
                               color,
                               font,
                               thickness=4,
                               display_str_list=()):
  """Adds a bounding box to an image."""
  draw = ImageDraw.Draw(image)
  im_width, im_height = image.size
  (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                ymin * im_height, ymax * im_height)
  draw.line([(left, top), (left, bottom), (right, bottom), (right, top),
             (left, top)],
            width=thickness,
            fill=color)

  # If the total height of the display strings added to the top of the bounding
  # box exceeds the top of the image, stack the strings below the bounding box
  # instead of above.
  display_str_heights = [font.getsize(ds)[1] for ds in display_str_list]
  # Each display_str has a top and bottom margin of 0.05x.
  total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

  if top > total_display_str_height:
    text_bottom = top
  else:
    text_bottom = top + total_display_str_height
  # Reverse list and print from bottom to top.
  for display_str in display_str_list[::-1]:
    text_width, text_height = font.getsize(display_str)
    margin = np.ceil(0.05 * text_height)
    draw.rectangle([(left, text_bottom - text_height - 2 * margin),
                    (left + text_width, text_bottom)],
                   fill=color)
    draw.text((left + margin, text_bottom - text_height - margin),
              display_str,
              fill="black",
              font=font)
    text_bottom -= text_height - 2 * margin


def draw_boxes(image, boxes, class_names ,scores, max_boxes=10, min_score=0.5, class_entities =None):
  """Overlay labeled boxes on an image with formatted scores and label names."""
  colors = list(ImageColor.colormap.values())

  try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Regular.ttf",
                              25)
  except IOError:
    print("Font not found, using default font.")
    font = ImageFont.load_default()

  for i in range(min(boxes.shape[0], max_boxes)):
    if scores[i] >= min_score:
      ymin, xmin, ymax, xmax = tuple(boxes[i])
    #   display_str = "{}: {}%".format(class_names[i],
    #                                  int(100 * scores[i]))
    #   color = colors[hash(class_names[i]) % len(colors)]
      display_str = "{}: {}%".format(class_entities[i],
                                     int(100 * scores[i]))
      color = colors[hash(class_entities[i]) % len(colors)]
      image_pil = Image.fromarray(np.uint8(image)).convert("RGB")
      draw_bounding_box_on_image(
          image_pil,
          ymin,
          xmin,
          ymax,
          xmax,
          color,
          font,
          display_str_list=[display_str])
      np.copyto(image, np.array(image_pil))
  return image


def test_code():
  data = get_json_data("/Users/chautruong/Desktop/AI-Course-Mr-Vinh/HCM_AI_Challenge/Data/ObjectsC00_V00/C00_V0000/000000.json")
  print(data["detection_scores"])

  boxes, class_names, scores, class_entities =get_json_objs(json_data=data)

  image_path = "/Users/chautruong/Desktop/AI-Course-Mr-Vinh/HCM_AI_Challenge/Data/KeyFramesC00_V00/C00_V0000/000000.jpg"
  img = load_img(image_path)
  image_with_boxes = draw_boxes(img.numpy(), boxes, class_names, scores, class_entities=class_entities)
  # print(type(image_with_boxes))
  display_image(image_with_boxes)
  # img_dest = "./test_img.jpg"
  result = Image.fromarray(image_with_boxes, 'RGB')
  result.save('my.png')
  result.show()