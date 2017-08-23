# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to web2py!")
    return dict(message=T('Hello World'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


    
def redirect_after_login(form):
	redirect(URL(r=request,f='viewallposts'))

auth.settings.login_onaccept.append(redirect_after_login)
auth.settings.register_onaccept.append(redirect_after_login)

@auth.requires_login()
def home():

    a = db(db.auth_user.id ==  auth.user_id).select(db.auth_user.ALL)
    return locals()

@auth.requires_login()
def homepage():

    id2 = request.args(0)
    a = db(db.auth_user.id ==  id2).select(db.auth_user.ALL)
    id1 = auth.user_id
    return locals()

@auth.requires_login()
def view_people():

    id1 = auth.user_id
    a = db(db.auth_user.id != auth.user_id).select(db.auth_user.ALL)
    return locals()

    
#-----------------------------------------posts------------------------------------------------------#
import re
@auth.requires_login()
def create_post():
#	form = SQLFORM(db.posts, deletable=True,upload=URL('download'), fields=['post_text', 'uploads'])
	form = SQLFORM.factory(
		Field('Post_Text', 'text'))            
	if form.process().accepted:
		db.posts.insert(post_text=form.vars.Post_Text)
		session.flash='Post created'
		redirect(URL(r=request,f='viewallposts'))
	elif form.errors:
		response.flash='Errors in form'
	return locals()

@auth.requires_login()
def viewmyposts():
	me = db(db.auth_user.id == auth.user_id).select(db.auth_user.first_name)[0]['first_name']
	p = db((db.posts.id > 0) & (db.posts.created_by == auth.user_id)).select(db.posts.ALL ,orderby=~db.posts.created_on)
	comments=db(db.comment_post.id > 0).select(db.comment_post.ALL ,orderby=~db.comment_post.created_on)
	return locals()

def viewallposts():
        user = auth.user_id
	p = db(db.posts.id > 0).select(db.posts.ALL ,orderby=~db.posts.created_on)
	comments=db(db.comment_post.id > 0).select(db.comment_post.ALL) 
	return locals()

@auth.requires_login()
def post1():
#add comments in viewallposts
	cid=request.vars.cid
	if cid!=None:
		prev=request.vars.prev+'?cid='+cid
	else:
		prev = request.vars.prev
	comment=request.vars.comment
	pid=request.vars.pid
	if type(comment) == list:
		comment =  comment[0]
	db.comment_post.insert(body=str(comment),postid=pid)
	redirect(URL(r=request,f=prev))
	return locals()
@auth.requires_login()


def post2():
#add comments in viewmyposts
	comment=request.vars.comment
	pid=request.vars.pid
	if type(comment) == list:
		comment =  comment[0]
	db.comment_post.insert(body=str(comment),postid=pid)
	redirect(URL(r=request,f='viewmyposts'))
	return locals()
#	return dict(form=SQLFORM(db.comment_post).process(),comments=db(db.comment_post).select())


@auth.requires_login()
def delpost():
	pid=request.vars.pid
	if request.vars.grp_id!=None:
		prev = request.vars.prev+'/'+request.vars.grp_id
	else : 
		prev = request.vars.prev
	db(db.posts.id == pid).delete()
	session.flash='Deleted !'
	redirect(URL(r=request,f=prev))
	return locals()

@auth.requires_login()
def editpost():
	pid = request.vars.pid
	if request.vars.grp_id!=None:
		prev = request.vars.prev+'/'+request.vars.grp_id
	else:
		prev = request.vars.prev
	pst = db(db.posts.id == pid).select(db.posts.ALL)[0]
	form = SQLFORM(db.posts,pid,deletable=True, fields=['post_text'])
#	form = SQLFORM.factory(
#		Field('Post_Text', 'text',default = pst['post_text']),            
#		Field('Attachment', 'upload')
#		)            
	if form.process().accepted:
		p = db(db.posts.id == pid).select(db.posts.ALL)[0]
                p.post_text = form.vars.post_text
		p.update_record()
		session.flash='Successfully Updated'
		redirect(URL(r=request,f=prev))
	elif form.errors:
		response.flash='Errors in form'
	return locals()

#----------------------- Update My Information --------------------------
def update_my_info():
	 form = SQLFORM(db.auth_user, auth.user_id)
	 if form.process().accepted:
		 response.flash = 'form accepted'	
       	 elif form.errors:
		response.flash='Errors in form'    
	 return dict(form=form)
	 redirect(URL(r=request,f = 'home'))


