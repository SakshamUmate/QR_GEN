from flask import Flask, request, redirect, url_for, flash, jsonify, send_file
import os
import pandas as pd
import qrcode
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

UPLOAD_FOLDER = 'uploads'
QR_FOLDER = 'qr_codes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# Email configuration
SENDER_EMAIL = "maharashtraday1@gmail.com"
SENDER_PASSWORD = "cbniqfglcojzyipd"
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def send_email(recipient_email, recipient_name, qr_img_bytes):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = f"Hello {recipient_name}, here is your Food Coupon"
    msg.add_header('Reply-To', SENDER_EMAIL)

    body = f"""\
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
        <h2 style="color: #0B5394;">Hello {recipient_name},</h2>
        <p>This is your food coupon.</p>
        <p>
        🎫 Please present the attached QR code at the food counter to claim your coupon.<br>
        This code is valid for one-time use only.
        </p>
        <p style="margin-top: 30px;">
        Warm regards,<br>
        <strong>The Event Team</strong><br>
        <em>{SENDER_EMAIL}</em>
        </p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    img = MIMEImage(qr_img_bytes)
    img.add_header('Content-Disposition', 'attachment', filename="coupon.png")
    msg.attach(img)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, 'contacts.csv')
            file.save(filepath)
            # Process CSV and generate QR codes
            df = pd.read_csv(filepath)
            df['Scanned'] = False  # Add scanned column
            for index, row in df.iterrows():
                qr_data = f"hello_{row['Name']}"
                qr = qrcode.make(qr_data)
                qr_path = os.path.join(QR_FOLDER, f"{row['Name']}.png")
                with open(qr_path, 'wb') as f:
                    qr.save(f)
                # Send email with QR code
                with open(qr_path, 'rb') as img_file:
                    img_bytes = img_file.read()
                send_email(row['Email'], row['Name'], img_bytes)
            # Save updated CSV with scanned column
            df.to_csv(filepath, index=False)
            flash('CSV processed, QR codes generated, and emails sent.')
            return redirect(url_for('upload_csv'))
    from flask import get_flashed_messages
    messages = get_flashed_messages()
    return render_template_string('''
    <!doctype html>
    <html>
    <head>
        <title>Upload CSV - QR Code App</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%);
                margin: 0;
                padding: 0;
                color: #333;
            }
            nav {
                background-color: #2c3e50;
                padding: 15px 30px;
                color: #ecf0f1;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            nav div {
                font-size: 1.5em;
                font-weight: 700;
                letter-spacing: 1px;
            }
            nav a {
                color: #ecf0f1;
                text-decoration: none;
                margin: 0 15px;
                font-weight: 600;
                font-size: 1em;
                transition: color 0.3s ease;
            }
            nav a:hover {
                color: #f39c12;
            }
            .container {
                max-width: 600px;
                margin: 50px auto;
                background: white;
                padding: 40px 50px;
                border-radius: 12px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            }
            h1 {
                text-align: center;
                color: #34495e;
                margin-bottom: 30px;
                font-weight: 700;
            }
            form {
                display: flex;
                flex-direction: column;
                gap: 20px;
                margin-top: 10px;
            }
            input[type="file"] {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 1em;
                transition: border-color 0.3s ease;
            }
            input[type="file"]:focus {
                border-color: #2980b9;
                outline: none;
            }
            input[type="submit"] {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 14px;
                border-radius: 8px;
                font-size: 18px;
                cursor: pointer;
                font-weight: 600;
                box-shadow: 0 4px 10px rgba(41, 128, 185, 0.4);
                transition: background-color 0.3s ease, box-shadow 0.3s ease;
            }
            input[type="submit"]:hover {
                background-color: #1c5980;
                box-shadow: 0 6px 15px rgba(28, 89, 128, 0.6);
            }
            .flash-message {
                background-color: #dff0d8;
                color: #3c763d;
                border: 1px solid #d6e9c6;
                padding: 15px 20px;
                border-radius: 8px;
                margin-bottom: 25px;
                text-align: center;
                font-weight: 600;
                box-shadow: 0 2px 6px rgba(60, 118, 61, 0.3);
            }
            .buttons {
                display: flex;
                justify-content: center;
                gap: 25px;
                margin-top: 30px;
            }
            .buttons a button {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 28px;
                border-radius: 8px;
                font-size: 18px;
                cursor: pointer;
                font-weight: 600;
                box-shadow: 0 4px 10px rgba(39, 174, 96, 0.4);
                transition: background-color 0.3s ease, box-shadow 0.3s ease;
            }
            .buttons a button:hover {
                background-color: #1e8449;
                box-shadow: 0 6px 15px rgba(30, 132, 73, 0.6);
            }
            @media (max-width: 640px) {
                .container {
                    margin: 20px;
                    padding: 30px 20px;
                }
                nav {
                    flex-direction: column;
                    gap: 10px;
                }
                nav a {
                    margin: 0 10px;
                    font-size: 0.9em;
                }
                .buttons {
                    flex-direction: column;
                    gap: 15px;
                }
                .buttons a button {
                    width: 100%;
                    padding: 14px 0;
                }
            }
        </style>
    </head>
    <body>
        <nav>
            <div>QR Code App</div>
            <div>
                <a href="/">Upload CSV</a>
                <a href="/verify">Verify QR</a>
                <a href="/download_csv">Download CSV</a>
            </div>
        </nav>
        <div class="container">
            <h1>Upload CSV file with Name and Email columns</h1>
            {% if messages %}
                <div class="flash-message">
                    {{ messages[0] }}
                </div>
            {% endif %}
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <input type="submit" value="Upload">
            </form>
            <div class="buttons">
                <a href="/verify"><button>Verify QR Code</button></a>
                <a href="/download_csv"><button>Download Updated CSV</button></a>
            </div>
        </div>
    </body>
    </html>
    ''', messages=messages)

# Route to verify QR code scan
@app.route('/verify/<name>', methods=['GET'])
def verify_qr(name):
    csv_path = os.path.join(UPLOAD_FOLDER, 'contacts.csv')
    if not os.path.exists(csv_path):
        return jsonify({"error": "CSV file not found"}), 404

    # Read CSV and check if QR code is already scanned
    df = pd.read_csv(csv_path)
    if name not in df['Name'].values:
        return jsonify({"error": "QR code not recognized"}), 404

    scanned_status = df.loc[df['Name'] == name, 'Scanned'].iloc[0]
    if scanned_status:
        return jsonify({"message": "QR code already used"}), 400

    # Mark as scanned
    df.loc[df['Name'] == name, 'Scanned'] = True
    df.to_csv(csv_path, index=False)

    return jsonify({"message": f"QR code for {name} verified and marked as used."})

from flask import render_template_string

@app.route('/verify', methods=['GET'])
def verify_page():
    # Serve a simple page with a button to open camera and scan QR code
    html_content = '''
    <!doctype html>
    <html>
    <head>
        <title>Verify QR Code</title>
        <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
        <style>
            #reader {
                width: 500px;
                margin: auto;
            }
            #result {
                margin-top: 20px;
                font-size: 1.2em;
                color: green;
                text-align: center;
            }
            #verify-btn {
                display: block;
                margin: 20px auto;
                padding: 10px 20px;
                font-size: 1.2em;
            }
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">Verify QR Code</h1>
        <button id="verify-btn">Verify QR</button>
        <a href="/"><button>Back to Upload</button></a>
        <div id="reader" style="display:none;"></div>
        <div id="result"></div>

        <script>
            const verifyBtn = document.getElementById('verify-btn');
            const reader = document.getElementById('reader');
            const resultDiv = document.getElementById('result');
            let html5QrcodeScanner;

            verifyBtn.addEventListener('click', () => {
                verifyBtn.style.display = 'none';
                reader.style.display = 'block';
                resultDiv.innerHTML = '';

                html5QrcodeScanner = new Html5Qrcode("reader");

                html5QrcodeScanner.start(
                    { facingMode: "environment" },
                    {
                        fps: 10,
                        qrbox: 250
                    },
                    qrCodeMessage => {
                        // Stop scanning once a QR code is detected
                        html5QrcodeScanner.stop().then(() => {
                            reader.style.display = 'none';
                            verifyBtn.style.display = 'block';

                            // Extract name from QR code text
                            // Assuming QR code text is like "hello_Name"
                            let name = qrCodeMessage;
                            if (name.startsWith("hello_")) {
                                name = name.substring(6);
                            }

                            // Call backend verify endpoint
                            fetch(`/verify/${encodeURIComponent(name)}`)
                                .then(response => response.json())
                                .then(data => {
                                    if (data.message) {
                                        resultDiv.style.color = 'green';
                                        resultDiv.innerText = data.message;
                                    } else if (data.error) {
                                        resultDiv.style.color = 'red';
                                        resultDiv.innerText = data.error;
                                    } else {
                                        resultDiv.style.color = 'red';
                                        resultDiv.innerText = 'Unknown response from server.';
                                    }
                                })
                                .catch(err => {
                                    resultDiv.style.color = 'red';
                                    resultDiv.innerText = 'Error verifying QR code.';
                                });
                        }).catch(err => {
                            resultDiv.style.color = 'red';
                            resultDiv.innerText = 'Failed to stop scanning.';
                        });
                    },
                    errorMessage => {
                        // ignore scan errors
                    }
                ).catch(err => {
                    resultDiv.style.color = 'red';
                    resultDiv.innerText = 'Unable to start scanning. Please allow camera access.';
                });
            });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/download_csv', methods=['GET'])
def download_csv():
    csv_path = os.path.join(UPLOAD_FOLDER, 'contacts.csv')
    if os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True)
    else:
        return "CSV file not found", 404

if __name__ == '__main__':
    app.run(debug=True)
