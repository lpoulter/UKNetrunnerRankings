import os
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import tournament_exports, db
from ..util.util import process_tournament
from flask.ext.uploads import UploadNotAllowed
from models import Tournament

tournament_bp = Blueprint('tournament', __name__, url_prefix='/tournament')


@tournament_bp.route('/upload/', methods=['GET', 'POST'])
#@login_required
def upload():
    if request.method == 'POST' and 'tournament_export' in request.files:
        tournament_export = request.files['tournament_export']
        tournament_export.seek(0, os.SEEK_END)
        if tournament_export.tell() == 0:
            flash('Please select a file to upload.', 'danger')
            return redirect(url_for('.upload'))
        tournament_export.seek(0)
        try:
            filename = tournament_exports.save(tournament_export)
        except UploadNotAllowed:
            flash('Please upload a NRTM or NRT export file.', 'danger')
            return redirect(url_for('.upload'))

        tournament_record = Tournament(filename)

        process_tournament(tournament_record)

        db.session.add(tournament_record)
        db.session.commit()

        return redirect(url_for('.view_tournament', tournament_id=tournament_record.id))

    return render_template('tournament/upload.html', title="Upload tournament results")


@tournament_bp.route('/<int:tournament_id>/')
def view_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    return render_template('tournament/page.html', tournament=tournament, title="Tournament")