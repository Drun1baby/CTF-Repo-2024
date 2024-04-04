const jwt = require('jsonwebtoken')

/**
 * 封装jwt token验证
 */
module.exports = class jwtClass {
  getToken (uid) {
    return jwt.sign({ // 生成token
      exp: Math.floor(Date.now() / 1000) + (60 * 60), // token十五分钟过期
      data: `${uid}pass`
    }, 'shhhhh')
  }

  tokenVerify (ctx) {
    return new Promise((resolve) => {
      const token = ctx.header.authorization
      jwt.verify(token, 'shhhhh', {}, function (err, decoded) {
        if (err) resolve(401)
        else resolve(200)
      })
    })
  }
}
