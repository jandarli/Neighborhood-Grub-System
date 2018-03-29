import json

import pydot

edges = (
    ("home", "login"),
    ("home", "logout"),
    ("home", "dish posts"),
    ("home", "dish requests"),
    ("home", "account"),
    ("home", "suggestion"),
    ("login", "signup"),
    ("login", "home"),
    ("dish posts", "post detail"),
    ("dish posts", "orders-requests"),
    ("dish posts", "create post"),
    ("dish requests", "request detail"),
    ("dish requests", "create request"),
    ("post detail", "chef profile"),
    ("orders-requests", "cancel order"),
    ("orders-requests", "create request"),
    ("orders-requests", "edit request"),
    ("orders-requests", "cancel request"),
    ("orders-requests", "create post"),
    ("orders-requests", "orders-requests-history"),
    ("orders-requests", "order feedback"),
    ("order feedback", "order complain"),
    ("account", "orders-requests"),
    ("account", "manage posts"),
    ("account", "edit chef profile"),
    ("account", "terminate"),
    ("account", "deposit"),
    ("account", "withdraw"),
    ("terminate", "account"),
    ("deposit", "account"),
    ("withdraw", "account"),
    ("chef profile", "post detail"),
    ("chef profile", "chef history"),
    ("edit chef profile", "chef profile"),
    ("manage posts", "cancel post"),
    ("manage posts", "edit post"),
    ("manage posts", "manage post orders"),
    ("edit post", "manage posts"),
    ("cancel post", "manage posts"),
    ("create request", "orders-requests"),
    ("edit request", "orders-requests"),
    ("cancel request", "orders-requests"),
    ("create post", "orders-requests"),
)

page_to_template_path = (
    ("home",                    "ngs/django-project/ngs/templates/ngs/index.html"),
    ("login",                   "ngs/django-project/ngs/templates/registration/login.html"),
    ("account",                 "ngs/django-project/accounts/templates/accounts/account.html"),
    ("suggestion",              "ngs/django-project/accounts/templates/accounts/suggestion.html"),
    ("signup",                  "ngs/django-project/accounts/templates/accounts/signup.html"),
    ("dish posts",              "ngs/django-project/dishes/templates/dishes/posts.html"),
    ("dish requests",           "ngs/django-project/dishes/templates/dishes/requests.html"),
    ("post detail",             "ngs/django-project/dishes/templates/dishes/post_detail.html"),
    ("orders-requests",         "ngs/django-project/dishes/templates/dishes/orders-requests.html"),
    ("orders-requests-history", "ngs/django-project/dishes/templates/dishes/orders-requests-history.html"),
    ("create post",             "ngs/django-project/dishes/templates/dishes/create_post.html"),
    ("request detail",          "ngs/django-project/dishes/templates/dishes/request_detail.html"),
    ("cancel request",          "ngs/django-project/dishes/templates/dishes/cancel_request.html"),
    ("edit post",               "ngs/django-project/dishes/templates/dishes/edit_post.html"),
    ("cancel order",            "ngs/django-project/dishes/templates/dishes/cancel_order.html"),
    ("chef profile",            "ngs/django-project/dishes/templates/dishes/chef_detail.html"),
    ("chef history",            "ngs/django-project/dishes/templates/dishes/chef_history.html"),
    ("edit chef profile",       "ngs/django-project/dishes/templates/dishes/edit_chef.html"),
    ("manage posts",            "ngs/django-project/dishes/templates/dishes/manage_posts.html"),
    ("create request",          "ngs/django-project/dishes/templates/dishes/create_post.html"),
    ("edit request",            "ngs/django-project/dishes/templates/dishes/edit_request.html"),
    ("suspended",               "ngs/django-project/accounts/templates/accounts/suspended.html"),
)

def main():

    graph = pydot.Dot(graph_type="digraph")

    for u, v in edges:
        edge = pydot.Edge(u, v)
        graph.add_edge(edge)
    else:
        graph.write_png("site-map.png")

if __name__ == "__main__":
    main()
