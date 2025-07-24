from flask import Blueprint, request, jsonify, render_template, url_for, redirect
from werkzeug.utils import secure_filename
import boto3, uuid
from app.models import db, Reel
from datetime import datetime, timezone
from dotenv import load_dotenv

BUCKET_NAME = 'foreversocial-media-uploads'  # S3 bucket name
reels = Blueprint('reels', __name__)
s3 = boto3.client('s3')
@reels.route('/reels/upload', methods=['POST'])
def upload_reel():
    user_id = request.form.get('user_id')
    caption = request.form.get('caption', '')
    video = request.files.get('video')

    if not video:
        return jsonify({"error": "No video file provided"}), 400


    filename = secure_filename(video.filename)
    file_extension = filename.rsplit('.', 1)[-1]
    unique_filename = f"reels{uuid.uuid4()}.{file_extension}"

    s3.upload_fileobj(video, 'foreversocial-media-uploads', unique_filename, ExtraArgs={"ContentType": video.content_type})
    video_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"

    new_reel = Reel(
        user_id=user_id,
        caption=caption,
        video_url=video_url,
        created_at=datetime.now(timezone.utc),
        views=0,
        likes=0,
        comments='',
    )
    db.session.add(new_reel)
    db.session.commit()

    return jsonify({"message": "Reel uploaded successfully", "video_url": video_url}), 201




@reels.route('/reels', methods=['GET'])
def get_reels():
    reels = Reel.query.all()
    return render_template('reels.html', reels=reels)


@reels.route('/reels/like/<int:reel_id>', methods=['POST'])
def like_reel(reel_id):
    reel = Reel.query.get_or_404(reel_id)
    reel.likes += 1
    db.session.commit()
    return redirect(url_for('reels.get_reels'))


@reels.route('/reels/comment/<int:reel_id>', methods=['POST'])
def comment_reel(reel_id):
    comment = request.form.get('comment')
    reel = Reel.query.get_or_404(reel_id)
    if reel.comments:
        reel.comments += f'\n{comment}'
    else:
        reel.comments = comment
    db.session.commit()
    return redirect(url_for('reels.get_reels'))

