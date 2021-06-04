from flask import (Blueprint, render_template, url_for,
                   flash, redirect, request, abort)
from flask_login import current_user, login_required
from flaskapp import db
from flaskapp.post.forms import CreatePostForm, UpdatePostForm
from flaskapp.models import Post


post_blueprint = Blueprint('post_blueprint', __name__)


@post_blueprint.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your Post has been submitted successfully.", 'success')
        return redirect(url_for('main_blueprint.home'))
    flash("When You Are Creating New Post Please Follow Community Guidelines.", 'primary')
    return render_template("create_post.html", title="Create Post", form=form)


@post_blueprint.route('/post/<int:post_id>')
def see_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("see_post.html", title=post.title, post=post)


@post_blueprint.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = UpdatePostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your Post Has Been Updated Successfully.', 'success')
        return redirect(url_for('post_blueprint.see_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template("update_post.html", title=f"Update Post", form=form)


@post_blueprint.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your Post Has Been Deleted Successfully.', 'success')
    return redirect(url_for('main_blueprint.home'))

