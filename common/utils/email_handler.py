"""manage sending certain emails"""

def send_user_exist_email(request):
    # TODO: fill this
    email = request.data.get("email")
    print("Email: user already exist")
    return
