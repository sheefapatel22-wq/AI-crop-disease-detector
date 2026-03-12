from flask import Flask, render_template, request
import os
from PIL import Image
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- IMAGE ANALYSIS -----------------

def detect_disease(image_path):
    img = Image.open(image_path).resize((256,256)).convert("RGB")
    arr = np.array(img).astype(float)

    r,g,b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    total = arr.shape[0]*arr.shape[1]

    green = np.sum((g>r)&(g>b))
    yellow = np.sum((r>160)&(g>160)&(b<130))
    brown = np.sum((r>130)&(g<110)&(b<110))
    dark = np.sum((r<60)&(g<60)&(b<60))

    green_p = green/total
    yellow_p = yellow/total
    brown_p = brown/total
    dark_p = dark/total

    brightness = np.mean((r+g+b)/3)
    texture = np.std(arr)

    if green_p>0.72 and brown_p<0.03 and yellow_p<0.03 and brightness>95:
        disease="Healthy Leaf"
        conf=green_p
        severity="None"
        badge="success"
        tips=[
            "Maintain regular irrigation",
            "Use organic compost",
            "Weekly crop monitoring",
            "Avoid over-fertilization"
        ]

    elif brown_p>0.10:
        disease="Leaf Blight"
        conf=brown_p
        severity="High"
        badge="danger"
        tips=[
            "Apply copper fungicide",
            "Remove infected leaves",
            "Avoid overhead watering",
            "Improve air circulation"
        ]

    elif yellow_p>0.08:
        disease="Leaf Rust"
        conf=yellow_p
        severity="Medium"
        badge="warning"
        tips=[
            "Add nitrogen fertilizer",
            "Use rust-resistant seeds",
            "Spray sulfur fungicide",
            "Monitor soil nutrients"
        ]

    elif dark_p>0.22 and brightness<90:
        disease="Severe Infection"
        conf=dark_p
        severity="Critical"
        badge="dark"
        tips=[
            "Immediate pesticide treatment",
            "Isolate infected crops",
            "Consult agriculture officer",
            "Soil sterilization recommended"
        ]

    elif texture>60:
        disease="Spot Disease"
        conf=texture/100
        severity="Medium"
        badge="info"
        tips=[
            "Use antibacterial spray",
            "Avoid leaf wetness",
            "Improve drainage",
            "Crop rotation advised"
        ]

    else:
        disease="Minor Symptoms"
        conf=max(brown_p,yellow_p,dark_p)
        severity="Low"
        badge="secondary"
        tips=[
            "Observe for 2–3 days",
            "Maintain proper sunlight",
            "Balanced fertilization",
            "Prevent water stagnation"
        ]

    confidence=round(conf*100,2)

    stats={
        "Green": round(green_p*100,2),
        "Yellow": round(yellow_p*100,2),
        "Brown": round(brown_p*100,2),
        "Dark": round(dark_p*100,2),
        "Brightness": round(float(brightness),2),
        "Texture": round(float(texture),2)
    }

    return disease,confidence,severity,badge,tips,stats


# ---------------- ROUTES -----------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    file=request.files['image']
    path=os.path.join(UPLOAD_FOLDER,file.filename)
    file.save(path)

    disease,confidence,severity,badge,tips,stats=detect_disease(path)

    return render_template('result.html',
                           image_path=path,
                           disease=disease,
                           confidence=confidence,
                           severity=severity,
                           badge=badge,
                           tips=tips,
                           stats=stats)


if __name__=='__main__':
    app.run(debug=True)