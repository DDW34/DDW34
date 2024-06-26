from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
from ultralytics import YOLO
import os
from werkzeug.utils import secure_filename
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi'}

model = YOLO('static/Yolo/best.pt')

descriptions = {
    'L-belok-kanan': 'Dilarang untuk belok ke kanan.',
    'L-belok-kiri': 'Dilarang untuk belok ke kiri.',
    'L-berhenti': 'Harus berhenti.',
    'L-berjalan-terus': 'Dilarang untuk berjalan terus atau harus stop.',
    'L-masuk': 'Dilarang masuk.',
    'L-parkir': 'Dilarang parkir.',
    'L-putar-balik': 'Dilarang putar balik.',
    'lampu-hijau': 'Lampu lalu lintas hijau, boleh melanjutkan perjalanan.',
    'lampu-kuning': 'Lampu lalu lintas kuning, siap-siap berhenti.',
    'lampu-merah': 'Lampu lalu lintas merah, harus berhenti.',
    'p-area-parkir': 'Area parkir.',
    'p-isyarat': 'Perhatikan isyarat.',
    'p-masuk-jalur': 'Boleh masuk ke jalur ini.',
    'p-masuk-kiri': 'Boleh masuk ke jalur kiri.',
    'p-pemberhentian-bus': 'Pemberhentian bus.',
    'p-penegasan': 'Penegasan.',
    'p-penyeberangan': 'Penyeberangan.',
    'p-perlintasan-kereta': 'Perlintasan kereta api.',
    'p-putar-balik': 'Putar balik.',
    'p-simpang-tiga': 'Simpang tiga.',
    'p-zebra-cross': 'Zebra cross, silakan berhenti untuk pejalan kaki.'
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            if file.filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi'}:
                # Deteksi video menggunakan model YOLO
                output_filename = 'hasil_' + filename
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                detect_video(file_path, output_path)
                result_descriptions = []
            else:
                # Deteksi gambar menggunakan model YOLO
                results = model(file_path)
                
                # Simpan gambar hasil deteksi dengan nama 'hasil'
                output_filename = 'hasil.png'
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                
                result_descriptions = []
                for result in results:
                    result_image = result.plot()  # Ambil gambar hasil deteksi
                    cv2.imwrite(output_path, result_image)  # Simpan gambar hasil deteksi
                    
                    for box in result.boxes:
                        class_name = model.names[int(box.cls)]
                        description = descriptions.get(class_name, 'Deskripsi tidak tersedia.')
                        result_descriptions.append((class_name, description))
            
            return render_template('index.html', 
                                   uploaded_file=filename, 
                                   result_file=output_filename,
                                   descriptions=result_descriptions)
    return render_template('index.html')

def detect_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Deteksi menggunakan model YOLO
        results = model(frame)
        result_frame = results[0].plot()
        
        out.write(result_frame)
    
    cap.release()
    out.release()

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Deteksi menggunakan model YOLO
            results = model(frame)
            result_frame = results[0].plot()
            
            ret, buffer = cv2.imencode('.jpg', result_frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
