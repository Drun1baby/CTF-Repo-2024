#!/bin/bash
password=`cat /proc/sys/kernel/random/uuid`
now=`date`
mongosh \
    -authenticationDatabase admin \
    -u $MONGO_INITDB_ROOT_USERNAME \
    -p $MONGO_INITDB_ROOT_PASSWORD \
    --eval "db.createUser({user: '$MONGO_INITDB_ROOT_USERNAME', pwd: '$MONGO_INITDB_ROOT_PASSWORD', roles: [{role: 'readWrite', db: 'wecat'}]});" wecat
mongosh \
    --authenticationDatabase admin \
    -u $MONGO_INITDB_ROOT_USERNAME \
    -p $MONGO_INITDB_ROOT_PASSWORD \
    --eval "db.user.insert({
    'nickName': 'admin',
    'trueName': 'admin',
    'pwd': '$password',
    'email': 'admin@wecat.com',
    'avatar': '',
    'access': 'admin',
    'time': '$now',
    'RecentlyTime': '$now'});" wecat
