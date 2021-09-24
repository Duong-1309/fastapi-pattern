import datetime
from app.utils.logger import get_stream_logger
from fastapi import Form, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from pymongo import ReturnDocument
from configs.settings import app, DB_NAME, MONGO_CLIENT, PROJECT_SECRET_KEY
from secure._token import create_access_token, is_expired,\
                          get_data_from_access_token
from secure._password import get_password_hashed, verify_password

from models.request.user import Token, User
from bson.objectid import ObjectId


logger = get_stream_logger(__name__)


@app.post(path='/account', tags=['account'])
async def create_account(
    email: EmailStr = Form(..., description='Email đăng kí'),
    username: str = Form(..., description='Họ tên'),
    password: str = Form(..., description='Mật khẩu'),
    re_password: str = Form(..., description='Nhập lại mật khẩu'),
    device_id: str = Form(..., description='Id thiết bị đăng kí'),
    # verification_link: str = Form(..., description='Link xác nhận tài khoản'),
):
    """Create the account in the system"""
    # Kiểm tra tài khoản đã có trong hệ thống hay chưa
    if MONGO_CLIENT[f'{DB_NAME}']['users'].find({'email': {'$eq': email}}).count():
        return JSONResponse(content={
            'status': 'Đã xảy ra lỗi!',
            'msg': 'Email đã tồn tại trong hệ thống'
        }, status_code=403)
    # Kiểm tra mật khẩu trùng khớp
    if password != re_password:
        return JSONResponse(
            content={
                'status': 'Đã xảy ra lỗi!',
                'msg': 'Mật khẩu không khớp'
            },
            status_code=400
        )
    # Tạo tài khoản
    access_token, secret_key = create_access_token(
        data={
            "username": username,
            "password": password
        }
    )
    token = Token(
        access_token=access_token,
        token_type='Bearer',
        device_id=device_id
    )
    user = User(
        username=username,
        tokens=[token],
        secret_key=secret_key,
        email=email,
        hashed_password=get_password_hashed(password),
        datetime_created=datetime.datetime.now(),
        is_verified=False,
        roles_id=[1]
    )
    inserted = MONGO_CLIENT[f'{DB_NAME}']['users'].insert_one(
        jsonable_encoder(user)
    ).inserted_id
    encoded_jwt, _ = create_access_token(
        {'user_id': str(inserted)},
        expires_delta=datetime.timedelta(minutes=30),
        secret_key=PROJECT_SECRET_KEY)
    # TODO: Send mail verify to the user
    # await create_account_verification('customer@sasamviet.com', email, data={
    #     'User_Name': username,
    #     'msg': 'Nhấn vào link hoặc nút xác nhận bên dưới để xác nhận tài khoản',
    #     'Verification_Link': f'{verification_link}?verifyKey={encoded_jwt}'
    # })
    return JSONResponse(
        content={
            'status': 'Tạo tài khoản thành công',
            'access_token': access_token,
            'secret_key': secret_key,
            'device_id': device_id,
            'is_verified': False,
            'verify_link': f'http://127.0.0.1:8000/account/verify?verify_key={encoded_jwt}'
        },
        status_code=201
    )


@app.get(path='/account/verify', tags=['account'])
async def verify_account(
    verify_key: str = Query(..., description='Key xác thực tài khoản')
):
    if not is_expired(verify_key, PROJECT_SECRET_KEY):
        data = get_data_from_access_token(verify_key, PROJECT_SECRET_KEY)
        user_id = data.get('user_id')
        _id = ObjectId(user_id)
        # Update status verify of the user
        MONGO_CLIENT[f'{DB_NAME}']['users'].find_one_and_update(
            filter={"_id": _id},
            update={
                "$set": {"is_verified": True}
            }
        )
        return JSONResponse(
            content={
                'status': 'Thành công!',
                'msg': 'Đã xác nhận tài khoản'
            },
            status_code=200
        )
    return JSONResponse(content={
        'status': 'Thất bại!',
        'msg': 'Key xác nhận đã hêt hạn hoặc không hợp lệ'
    }, status_code=403)


@app.post(path='/account/login', tags=['account'])
async def login(
    email: EmailStr = Form(..., description='Email'),
    password: str = Form(..., description='Mật khẩu'),
    device_id: str = Form(..., description='Id thiết bị đăng nhập')
):
    try:
        user = MONGO_CLIENT[f'{DB_NAME}']['users'].find_one(
            {'email': {'$eq': email}}
        )
        if not user or not verify_password(password, user.get('hashed_password')):
            raise Exception('Email hoặc mật khẩu sai', 400)
        if not user.get('is_verified'):
            raise Exception('Tài khoản của bạn chưa được xác thưc', 403)
        # create new access token for device
        secret_key = user.get('secret_key')
        access_token, _ = create_access_token(
            {'email': user.get('email'), 'username': user.get('username')},
            secret_key=secret_key
        )
        token = Token(
            access_token=access_token,
            token_type='Bearer',
            device_id=device_id
        )
        # check device logged
        if device_id in [_token.get('device_id') for _token in user.get('tokens')]:
            MONGO_CLIENT[f'{DB_NAME}']['users'].find_one_and_update(
                filter={
                    '$and': [
                        {'email': {'$eq': email}},
                        {'device_id': {'$eq': device_id}}
                    ]
                },
                update={
                    '$set': {'token.$': jsonable_encoder(token)}
                }
            )
            roles = list()
            _roles = MONGO_CLIENT[f'{DB_NAME}']['roles'].find(
                {"role_id": {'$in': user.get("roles_id") or []}},
                {"_id": False}
            )
            for _role in _roles:
                roles.append(_role)
            return JSONResponse(
                content={
                    'token': jsonable_encoder(token),
                    'secret_key': secret_key,
                    'username': user.get('username'),
                    'uid': str(user.get('_id')),
                    'roles': roles
                },
                status_code=200
            )
        else:
            if len(user.get('tokens')) >= 5:
                raise Exception('Đã quá giới hạn thiết bị đăng nhập', 403)
            user = MONGO_CLIENT[f'{DB_NAME}']['users'].find_one_and_update(
                filter={"email": {"$eq": email}},
                update={
                    "$push": {"tokens": jsonable_encoder(token)}
                },
                return_document=ReturnDocument.AFTER
            )
            return JSONResponse(content={
                'token': jsonable_encoder(token),
                'secret_key': secret_key
            }, status_code=200)
    except Exception as e:
        msg, code = e.args if len(e.args) == 2 else e.args, None
        return JSONResponse(
            content={
                'status': 'Đã xảy ra lỗi!',
                'msg': f'{msg}'
            },
            status_code=code if code else 400
        )
