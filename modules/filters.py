from flask import session


def set_filter_list(filter_type,value):
    print(f'adding filter to: {filter_type}="{value}"')
    current=session.get(filter_type)
    if current is None:
        current = set()
    else:
        current = set(current)
        
    if value.id in current:
        current.remove(value.id)
    else:
        current.add(value.id)
    session[filter_type]= list(current)
    print(current)

def remove_filter_list(filter_type,value):
    print(f'removing filter: {filter_type}="{value.id}"')
    current=set(session.get(filter_type))
    if current:
        current.remove(value.id)
        session[filter_type]=list(current)
        print(f' after removal {current}')

def get_filter_list_ids(filter_type):
    current=session.get(filter_type)
    return current if current else []


def set_filter(filter_type,value):
    print(f'set_filter: {filter_type}="{value}"')
    current = session.get(filter_type) 
    if current==value:
        session[filter_type]=None
    else: 
        session[filter_type]=value

def get_filter(filtertype):
    return session.get(filtertype)

def remove_filters(filters):
    for filter in filters:
        set_filter(filter,None)
