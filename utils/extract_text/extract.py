from google.cloud import vision

'''
"extract_text" extract scripts from cartoon image

[Parameter]
  - path
      - image file path in server file system

[Return value]
this function return array of dictionary that conatains scripts and bounding box information each
  
  - script
    - extracted script from image
    - It doesn't distinguish between sound effects and characters' scripts

  - bounding box
    - bounding box point of scripts
    - function caller needs to distinguish each scirpts are character's or not 
    - bounding box points are saved in the order of upper left, upper right, lower right, and lower left
'''
def extract_text(path):
    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        image_content = image_file.read()
    
    image = vision.Image(content=image_content)

    try:
        response = client.text_detection(image=image)
    except Exception as e:
        return {"error" : True, "data" : f"Cannot make response with module: {e}"}
    
    if response.error.message:
        return {"error" : True, "data" : f"{response.error.message}"}
    
    ## No error has occurred, but the performance is uncertain
    texts = response.text_annotations
    
    data = process_text(texts=texts)
    if not data:
        return {"error" : True, "data" : f"No text detected in image"}
    
    return {"error" : False, "data" : data}

def process_text(texts):
    ret = []
    for text in texts:
        vertices = [{"x" : vertex.x, "y" : vertex.y} for vertex in text.bounding_poly.vertices]
        text_data = {"script" : text.description, "bounding_box" : vertices}

        ret.append(text_data)
    
    ## first object contains ALL SCRIPTS in image
    ret = ret[1:]
    return ret