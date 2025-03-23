import os
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
import webbrowser
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages
socketio = SocketIO(app)  # Add SocketIO support

# Global variables to store parsed data and HTML structure
video_data = []
soup = None
html_file_path = ''

def parse_html(file_path):
    global soup, video_data, html_file_path
    html_file_path = file_path
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'html.parser')
    video_divs = soup.find_all('div', class_='video')
    
    video_data.clear()
    for div in video_divs:
        entry = {
            'href': div.find('a')['href'] if div.find('a') else '',
            'img_src': div.find('img')['src'] if div.find('img') else '',
            'title': div.find('h2', class_='video-title').text if div.find('h2', class_='video-title') else ''
        }
        video_data.append(entry)

def save_changes():
    global soup, html_file_path, video_data
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'html.parser')
    
    video_divs = soup.find_all('div', class_='video')
    parent = video_divs[0].parent if video_divs else soup.body
    for div in video_divs:
        div.decompose()
    
    for video in video_data:
        new_div = soup.new_tag('div', **{'class': 'video'})
        
        a_tag = soup.new_tag('a', href=video['href'], target='_blank')
        img_tag = soup.new_tag('img', src=video['img_src'], loading='lazy')
        a_tag.append(img_tag)
        
        h2_tag = soup.new_tag('h2', **{'class': 'video-title'})
        h2_tag.string = video['title']
        
        new_div.append(a_tag)
        new_div.append(h2_tag)
        parent.append(new_div)
    
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    
    parse_html(html_file_path)
    return True

# Add new function to update a specific video element without adding a duplicate.
def update_element(index):
    global html_file_path, video_data
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        video_divs = soup.find_all('div', class_='video')
        if index >= len(video_divs):
            return False
        video_div = video_divs[index]
        video = video_data[index]
        
        # Update the link
        a_tag = video_div.find('a') or soup.new_tag('a')
        a_tag['href'] = video['href']
        a_tag['target'] = '_blank'
        
        # Update the image source
        img_tag = video_div.find('img') or soup.new_tag('img')
        img_tag['src'] = video['img_src']
        img_tag['loading'] = 'lazy'
        if not video_div.find('img'):
            a_tag.append(img_tag)
        
        # Update the video title
        h2_tag = video_div.find('h2', class_='video-title') or soup.new_tag('h2', **{'class': 'video-title'})
        h2_tag.string = video['title']
        
        if not video_div.find('a'):
            video_div.append(a_tag)
        if not video_div.find('h2'):
            video_div.append(h2_tag)
            
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        return True
    except Exception as e:
        print(f"Error in update_element: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Video Editor</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
            <style>
                .video-card { transition: transform 0.2s; margin-bottom: 1.5rem; }
                .video-card:hover { transform: translateY(-5px); }
                .video-thumbnail { height: 200px; object-fit: cover; border-radius: 8px; }
                .edit-btn { width: 100px; }
                .alert { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 1000; }
            </style>
        </head>
        <body class="bg-light">
            <div class="container py-5">
                <h1 class="mb-4 text-center text-primary">Video Content Manager</h1>

                <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4" id="videoGrid">
                    {% for video in videos %}
                        <div class="col" id="video-{{ loop.index0 }}">
                            <div class="card h-100 video-card shadow-sm">
                                <img src="{{ video.img_src }}" class="card-img-top video-thumbnail" alt="Thumbnail">
                                <div class="card-body">
                                    <h5 class="card-title">{{ video.title }}</h5>
                                    <a href="{{ video.href }}" target="_blank" class="btn btn-sm btn-outline-primary mb-2">
                                        View Link
                                    </a>
                                    <div class="d-grid gap-2">
                                        <button onclick="openEditModal({{ loop.index0 }})" class="btn btn-primary edit-btn">
                                            <i class="bi bi-pencil"></i> Edit
                                        </button>
                                        <button onclick="confirmDelete({{ loop.index0 }})" class="btn btn-danger">
                                            <i class="bi bi-trash"></i> Delete
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Edit Modal -->
            <div class="modal fade" id="editModal" tabindex="-1" aria-labelledby="editModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="editModalLabel"><i class="bi bi-pencil-square"></i> Edit Video Entry</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <form id="editForm" onsubmit="saveChanges(event)">
                                <input type="hidden" id="editIndex" name="index">
                                <div class="mb-3">
                                    <label class="form-label">Title</label>
                                    <input type="text" class="form-control" id="editTitle" name="title" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Image URL</label>
                                    <input type="url" class="form-control" id="editImgSrc" name="img_src" required
                                           onchange="document.getElementById('previewImage').src = this.value">
                                    <div class="mt-2">
                                        <img id="previewImage" src="" alt="Image preview" class="img-thumbnail" style="max-width: 300px;">
                                    </div>
                                </div>
                                <div class="mb-4">
                                    <label class="form-label">Link URL</label>
                                    <input type="url" class="form-control" id="editHref" name="href" required>
                                </div>
                                <div class="d-flex justify-content-end gap-2">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                    <button type="submit" class="btn btn-success">
                                        <i class="bi bi-save"></i> Save Changes
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
            <script>
                const socket = io();

                socket.on('video_updated', function(data) {
                    const videoCard = document.getElementById(`video-${data.index}`);
                    videoCard.querySelector('.card-title').textContent = data.data.title;
                    videoCard.querySelector('img').src = data.data.img_src;
                    videoCard.querySelector('.btn-outline-primary').href = data.data.href;
                });

                socket.on('video_deleted', function(data) {
                    const videoElement = document.getElementById(`video-${data.index}`);
                    if (videoElement) {
                        videoElement.remove();
                    }
                });

                let currentIndex = null;

                function openEditModal(index) {
                    currentIndex = index;
                    const video = {{ videos|tojson }};
                    document.getElementById('editIndex').value = index;
                    document.getElementById('editTitle').value = video[index].title;
                    document.getElementById('editImgSrc').value = video[index].img_src;
                    document.getElementById('editHref').value = video[index].href;
                    document.getElementById('previewImage').src = video[index].img_src;

                    new bootstrap.Modal(document.getElementById('editModal')).show();
                }

                async function saveChanges(event) {
                    event.preventDefault();
                    const formData = new FormData(event.target);
                    const data = Object.fromEntries(formData.entries());

                    try {
                        const response = await fetch(`/edit/${currentIndex}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(data)
                        });

                        if (response.ok) {
                            // Update UI
                            const videoCard = document.getElementById(`video-${currentIndex}`);
                            videoCard.querySelector('.card-title').textContent = data.title;
                            videoCard.querySelector('img').src = data.img_src;
                            videoCard.querySelector('.btn-outline-primary').href = data.href;

                            bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
                            showAlert('Changes saved successfully!', 'success');
                        } else {
                            throw new Error('Failed to save changes');
                        }
                    } catch (error) {
                        console.error(error);
                        showAlert('Error saving changes!', 'danger');
                    }
                }

                async function confirmDelete(index) {
                    if (confirm('Are you sure you want to delete this entry?')) {
                        try {
                            const response = await fetch(`/delete/${index}`, {
                                method: 'DELETE'
                            });

                            if (response.ok) {
                                // Remove the deleted element from DOM
                                const videoElement = document.getElementById(`video-${index}`);
                                if (videoElement) {
                                    videoElement.remove();
                                    showAlert('Entry deleted successfully!', 'success');
                                }
                            } else {
                                throw new Error('Failed to delete entry');
                            }
                        } catch (error) {
                            console.error(error);
                            showAlert('Error deleting entry!', 'danger');
                        }
                    }
                }

                function showAlert(message, type) {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
                    alertDiv.role = 'alert';
                    alertDiv.innerHTML = `
                        ${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    `;

                    // Remove existing alerts
                    const existingAlerts = document.querySelectorAll('.alert');
                    existingAlerts.forEach(alert => alert.remove());

                    document.body.appendChild(alertDiv);

                    // Auto-remove alert after 3 seconds
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 3000);
                }
            </script>
        </body>
        </html>
    ''', videos=video_data)

@app.route('/edit/<int:index>', methods=['POST'])
def edit(index):
    if not html_file_path or not os.path.exists(html_file_path):
        return jsonify({'error': 'No HTML file loaded'}), 400
    
    if index >= len(video_data):
        return jsonify({'error': 'Invalid index'}), 400

    try:
        data = request.get_json()
        if not all(key in data for key in ['title', 'img_src', 'href']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        video_data[index] = {
            'title': data['title'],
            'img_src': data['img_src'],
            'href': data['href']
        }
        
        if update_element(index):
            # Broadcast the update to all clients
            socketio.emit('video_updated', {'index': index, 'data': video_data[index]})
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete/<int:index>', methods=['DELETE'])
def delete(index):
    if index < len(video_data):
        try:
            del video_data[index]
            if save_changes():
                # Broadcast the deletion to all clients
                socketio.emit('video_deleted', {'index': index})
                return jsonify({'success': True})
            return jsonify({'error': 'Save failed'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Invalid index'}), 400

if __name__ == '__main__':
    file_path = input("Enter the path to your HTML file: ")
    if not os.path.isfile(file_path):
        print("File not found!")
        exit()

    parse_html(file_path)
    webbrowser.open('http://localhost:5000')
    socketio.run(app, debug=True, use_reloader=False)