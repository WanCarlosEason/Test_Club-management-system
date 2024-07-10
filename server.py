from flask import Flask, request, render_template, redirect, url_for, session
import pymysql
import re

# 初始化 Flask 应用
app = Flask(__name__)
app.secret_key = 'carson'  # 添加一个密钥用于会话保护

# 使用 pymysql.connect 方法连接本地 mysql 数据库
db = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='123456',
    database='club_management_system',
    charset='utf8mb4'
)
# 操作数据库，获取 db 下的 cursor 对象
cursor = db.cursor()

# 登录路由处理
@app.route("/", methods=["GET", "POST"])
def login():
    # 检查是否是登出请求
    if request.args.get('action') == 'logout':
        session.clear()  # 清除所有会话数据
        return redirect(url_for('login'))

    # 增加会话保护机制(未登录前 login 的 session 值为空)
    session['login'] = ''
    msg = ''  # 默认消息为空
    if request.method == 'POST':
        user_account = request.values.get("user_account", "")
        pwd = request.values.get("user_password", "")
        result_user = re.search(r"^[a-zA-Z]+$", user_account)  # 限制用户名为全字母
        result_pwd = re.search(r"^[a-zA-Z\d]+$", pwd)  # 限制密码为字母和数字的组合
        if result_user is not None and result_pwd is not None:  # 验证通过
            sql1 = "SELECT * FROM user_login WHERE user_account=%s AND user_password=%s;"
            cursor.execute(sql1, (user_account, pwd))
            result = cursor.fetchone()
            # 匹配得到结果即管理员数据库中存在此用户
            if result:
                # 登陆成功
                session['login'] = 'OK'
                session['user'] = {'account': user_account, 'name': result[2], 'power': result[4]}  # 存储用户信息在会话中
                return redirect(url_for('admin_page_student'))
            else:
                msg = '用户名或密码错误'
        else:  # 输入验证不通过
            msg = '非法输入'
    else:
        user_account = ''
    return render_template('Club_login.html', msg=msg, user=user_account)

# # 用户页面路由处理
# @app.route("/user_page_Student")
# def user_page():
#     if session.get('login') == 'OK' and session.get('user')['power'] == 1:
#         return render_template('user_page_Student.html', user=session.get('user')['name'])
#     else:
#         return redirect(url_for('login'))

@app.route("/admin_page_Student", methods=["GET", "POST"])
def admin_page_student():
    # 修改了权限检查，允许权限1和权限2的用户访问
    if session.get('login') == 'OK' and session.get('user')['power'] in [1, 2]:
        user_power = session.get('user')['power']  # 获取用户的权限，并传递给前端
        
        if request.method == 'POST':
            # 处理表单提交的数据
            student_id = request.form.get('student_id')
            student_class = request.form.get('student_class')
            student_name = request.form.get('student_name')
            student_sex = request.form.get('student_sex')
            club_name = request.form.get('club_name')

            if not student_id or not student_class or not student_name or not student_sex or not club_name:
                return render_template('admin_page_Student.html', user=session.get('user')['name'], user_power=user_power, insert_result='请填写完整信息', results=[])

            try:
                sql = "INSERT INTO students (student_id, student_class, student_name, student_sex, student_club) VALUES (%s, %s, %s, %s, %s);"
                cursor.execute(sql, (student_id, student_class, student_name, student_sex, club_name))
                db.commit()
                insert_result = '成功插入学生信息'
            except Exception as e:
                print(e)
                db.rollback()
                insert_result = '插入失败，请重试'

            # 重新获取最新的学生信息列表
            sql = "SELECT * FROM students;"
            cursor.execute(sql)
            results = cursor.fetchall()

            # 渲染模板时传递 user_power
            return render_template('admin_page_Student.html', user=session.get('user')['name'], user_power=user_power, results=results, insert_result=insert_result)
        
        else:
            # GET 请求时，渲染页面并获取需要的数据
            sql = "SELECT * FROM students;"
            cursor.execute(sql)
            results = cursor.fetchall()

            # 渲染模板时传递 user_power
            return render_template('admin_page_Student.html', user=session.get('user')['name'], user_power=user_power, results=results, insert_result='')
    
    else:
        return redirect(url_for('login'))  # 未登录或权限不足，重定向到登录页面


# 管理员社团信息录入页面路由处理
@app.route("/admin_page_Club", methods=["GET", "POST"])
def admin_page_club():
    # 修改了权限检查，允许权限1和权限2的用户访问
    if session.get('login') == 'OK' and session.get('user')['power'] in [1, 2]:
        user_power = session.get('user')['power']  # 获取用户的权限，并传递给前端
        if request.method == 'POST':
            # 处理表单提交的数据
            club_name = request.form.get('club_name')
            club_advisor = request.form.get('club_advisor')

            if not club_name or not club_advisor:
                return render_template('admin_page_Club.html', user=session.get('user')['name'], user_power=user_power, insert_result='请填写完整信息')

            try:
                sql = "INSERT INTO clubs (club_name, club_advisor) VALUES (%s, %s);"
                cursor.execute(sql, (club_name, club_advisor))
                db.commit()
                insert_result = '成功插入社团信息'
            except Exception as e:
                print(e)
                db.rollback()
                insert_result = '插入失败，请重试'

            # 重新获取最新的社团信息列表
            sql = "SELECT * FROM clubs;"
            cursor.execute(sql)
            results = cursor.fetchall()

            return render_template('admin_page_Club.html', user=session.get('user')['name'], user_power=user_power, results=results, insert_result=insert_result)

        else:
            # GET 请求时，渲染页面并获取需要的数据
            sql = "SELECT * FROM clubs;"
            cursor.execute(sql)
            results = cursor.fetchall()
            return render_template('admin_page_Club.html', user=session.get('user')['name'], user_power=user_power, results=results)
    else:
        return redirect(url_for('login'))  # 未登录或权限不足，重定向到登录页面

@app.route("/admin_page_UserManagement", methods=["GET", "POST"])
def admin_page_user_management():
    def get_admin_users():
        sql_select = "SELECT * FROM user_login;"
        cursor.execute(sql_select)
        return cursor.fetchall()

    # 修改了权限检查，允许权限1和权限2的用户访问
    if session.get('login') == 'OK' and session.get('user')['power'] in [1, 2]:
        user_power = session.get('user')['power']  # 获取用户的权限，并传递给前端
        if request.method == 'POST':
            selected_action = request.form.get('selected_one')

            if selected_action == '增加管理员':
                admin_account = request.form.get('admin_account')
                admin_name = request.form.get('admin_name')
                admin_password = request.form.get('admin_password')
                admin_power = request.form.get('admin_power')

                # 验证是否存在相同账号或用户名
                sql_check_exist = "SELECT * FROM user_login WHERE user_account = %s OR user_name = %s;"
                cursor.execute(sql_check_exist, (admin_account, admin_name))
                if cursor.fetchone():
                    return render_template('admin_page_UserManagement.html', user=session.get('user')['name'], user_power=user_power, insert_result='账号或用户名已存在', results=get_admin_users())

                # 插入新管理员信息
                try:
                    sql_insert = "INSERT INTO user_login (user_account, user_name, user_password, power) VALUES (%s, %s, %s, %s);"
                    cursor.execute(sql_insert, (admin_account, admin_name, admin_password, admin_power))
                    db.commit()
                    insert_result = '成功添加管理员'
                except Exception as e:
                    print(e)
                    db.rollback()
                    insert_result = '添加管理员失败，请重试'

            elif selected_action == '修改管理员信息':
                admin_account = request.form.get('admin_account')
                admin_name = request.form.get('admin_name')
                admin_password = request.form.get('admin_password')
                admin_power = request.form.get('admin_power')

                # 更新管理员信息
                try:
                    sql_update = "UPDATE user_login SET user_name = %s, user_password = %s, power = %s WHERE user_account = %s;"
                    cursor.execute(sql_update, (admin_name, admin_password, admin_power, admin_account))
                    db.commit()
                    insert_result = '成功修改管理员信息'
                except Exception as e:
                    print(e)
                    db.rollback()
                    insert_result = '修改管理员信息失败，请重试'

            elif selected_action == '删除管理员':
                admin_account = request.form.get('admin_account')

                # 删除管理员
                try:
                    sql_delete = "DELETE FROM user_login WHERE user_account = %s;"
                    cursor.execute(sql_delete, (admin_account,))
                    db.commit()
                    insert_result = '成功删除管理员'
                except Exception as e:
                    print(e)
                    db.rollback()
                    insert_result = '删除管理员失败，请重试'

            # 获取最新的管理员列表
            results = get_admin_users()
            return render_template('admin_page_UserManagement.html', user=session.get('user')['name'], user_power=user_power, results=results, insert_result=insert_result)

        else:
            # GET 请求时，获取管理员列表并渲染页面
            results = get_admin_users()
            return render_template('admin_page_UserManagement.html', user=session.get('user')['name'], user_power=user_power, results=results)

    else:
        return redirect(url_for('login'))  # 未登录或权限不足，重定向到登录页面

# 学生信息管理页面路由处理
@app.route("/admin_page_StudentManagement", methods=["GET", "POST"])
def admin_page_student_management():
    # 修改了权限检查，允许权限1和权限2的用户访问
    if session.get('login') == 'OK' and session.get('user')['power'] in [1, 2]:
        user_power = session.get('user')['power']  # 获取用户的权限，并传递给前端
        # 获取所有学生信息的函数
        def get_students():
            sql = "SELECT * FROM students;"
            cursor.execute(sql)
            return cursor.fetchall()

        if request.method == 'POST':
            selected_action = request.form.get('selected_one')

            if selected_action == '修改学生信息':
                student_id = request.form.get('student_id')
                student_class = request.form.get('student_class')
                student_name = request.form.get('student_name')
                student_sex = request.form.get('student_sex')
                student_club = request.form.get('student_club')

                # 更新学生信息
                try:
                    sql_update = "UPDATE students SET student_class = %s, student_name = %s, student_sex = %s, student_club = %s WHERE student_id = %s;"
                    cursor.execute(sql_update, (student_class, student_name, student_sex, student_club, student_id))
                    db.commit()
                    insert_result = '成功修改学生信息'
                except Exception as e:
                    print(e)
                    db.rollback()
                    insert_result = '修改学生信息失败，请重试'

            elif selected_action == '删除学生信息':
                student_id = request.form.get('student_id')

                # 删除学生信息
                try:
                    sql_delete = "DELETE FROM students WHERE student_id = %s;"
                    cursor.execute(sql_delete, (student_id,))
                    db.commit()
                    insert_result = '成功删除学生信息'
                except Exception as e:
                    print(e)
                    db.rollback()
                    insert_result = '删除学生信息失败，请重试'

            # 获取最新的学生列表
            results = get_students()
            return render_template('admin_page_StudentManagement.html', user=session.get('user')['name'], user_power=user_power, results=results, insert_result=insert_result)

        else:
            # GET 请求时，获取学生列表并渲染页面
            results = get_students()
            return render_template('admin_page_StudentManagement.html', user=session.get('user')['name'], user_power=user_power, results=results)

    else:
        return redirect(url_for('login'))  # 未登录或权限不足，重定向到登录页面

@app.route("/admin_page_StudentQuery", methods=["GET", "POST"])
def admin_page_student_query():
    # 修改了权限检查，允许权限1和权限2的用户访问
    if session.get('login') == 'OK' and session.get('user')['power'] in [1, 2]:
        user_power = session.get('user')['power']  # 获取用户的权限，并传递给前端
        if request.method == 'POST':
            student_id = request.form.get('student_id').strip()
            student_class = request.form.get('student_class').strip()
            student_name = request.form.get('student_name').strip()
            student_sex = request.form.get('student_sex').strip()
            club_name = request.form.get('club_name').strip()

            # 构建查询条件
            conditions = []
            parameters = []
            if student_id:
                conditions.append("student_id = %s")
                parameters.append(student_id)
            if student_class:
                conditions.append("student_class = %s")
                parameters.append(student_class)
            if student_name:
                conditions.append("student_name = %s")
                parameters.append(student_name)
            if student_sex:
                conditions.append("student_sex = %s")
                parameters.append(student_sex)
            if club_name:
                conditions.append("student_club = %s")
                parameters.append(club_name)

            if conditions:
                sql_query = "SELECT * FROM students WHERE " + " AND ".join(conditions) + ";"
                cursor.execute(sql_query, parameters)
                results = cursor.fetchall()
                if results:
                    query_result = '查询成功'
                else:
                    query_result = '查询失败'
            else:
                results = []
                query_result = '请至少输入一个查询条件'
            
            return render_template('admin_page_StudentQuery.html', user=session.get('user')['name'], user_power=user_power, results=results, query_result=query_result)

        else:
            # GET 请求时，直接渲染页面，不显示任何查询结果
            return render_template('admin_page_StudentQuery.html', user=session.get('user')['name'], user_power=user_power, results=[], query_result='')

    else:
        return redirect(url_for('login'))  # 未登录或权限不足，重定向到登录页面

@app.route("/activity_application", methods=["GET", "POST"])
def activity_application():
    # 修改了权限检查，允许权限1和权限2的用户访问
    if session.get('login') == 'OK' and session.get('user')['power'] in [1, 2]:
        user_power = session.get('user')['power']  # 获取用户的权限，并传递给前端
        insert_result = ''  # 在函数的开头初始化 insert_result 变量
        if request.method == 'POST':
            club_id = request.form.get('club_id').strip()
            club_name = request.form.get('club_name').strip()
            activity_name = request.form.get('activity_name').strip()
            venue = request.form.get('venue').strip()
            activity_time = request.form.get('activity_time').strip()

            # 插入活动申请信息，默认未批准
            try:
                sql_insert = """
                    INSERT INTO club_activity_applications (club_id, club_name, activity_name, venue, activity_time, approved) 
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                cursor.execute(sql_insert, (club_id, club_name, activity_name, venue, activity_time, '否'))
                db.commit()
                insert_result = '活动申请提交成功'
            except Exception as e:
                print(e)
                db.rollback()
                insert_result = '活动申请提交失败，请重试'

        # 获取所有活动申请记录
        sql_select = "SELECT * FROM club_activity_applications;"
        cursor.execute(sql_select)
        results = cursor.fetchall()
        
        return render_template('activity_application.html', user=session.get('user')['name'], user_power=user_power, results=results, insert_result=insert_result)
    
    else:
        return redirect(url_for('login'))  # 未登录，重定向到登录页面

    
@app.route("/admin_page_ClubQuery", methods=["GET", "POST"])
def admin_page_club_query():
    # 修改了权限检查，允许权限1和权限2的用户访问
    if session.get('login') == 'OK' and session.get('user')['power'] in [1, 2]:
        user_power = session.get('user')['power']  # 获取用户的权限，并传递给前端
        if request.method == 'POST':
            club_id = request.form.get('club_id').strip()
            club_name = request.form.get('club_name').strip()
            club_advisor = request.form.get('club_advisor').strip()
            member_count = request.form.get('member_count').strip()

            # 构建查询条件
            conditions = []
            parameters = []
            if club_id:
                conditions.append("club_id = %s")
                parameters.append(club_id)
            if club_name:
                conditions.append("club_name = %s")
                parameters.append(club_name)
            if club_advisor:
                conditions.append("club_advisor = %s")
                parameters.append(club_advisor)
            if member_count:
                conditions.append("member_count = %s")
                parameters.append(member_count)

            if conditions:
                sql_query = "SELECT * FROM clubs WHERE " + " AND ".join(conditions) + ";"
                cursor.execute(sql_query, parameters)
                results = cursor.fetchall()
                query_result = '查询成功'
            else:
                results = []
                query_result = '请至少输入一个查询条件'

            return render_template('admin_page_ClubQuery.html', user=session.get('user')['name'], user_power=user_power, results=results, query_result=query_result)

        else:
            # GET 请求时，直接渲染页面，不显示任何查询结果
            return render_template('admin_page_ClubQuery.html', user=session.get('user')['name'], user_power=user_power, results=[], query_result='')

    else:
        return redirect(url_for('login'))  # 未登录或权限不足，重定向到登录页面

@app.route("/admin_page_ActivityApproval", methods=["GET", "POST"])
def admin_page_activity_approval():
    # 修改了权限检查，允许权限1和权限2的用户访问
    if session.get('login') == 'OK' and session.get('user')['power'] in [1, 2]:
        user_power = session.get('user')['power']  # 获取用户的权限，并传递给前端
        if request.method == 'POST':
            action = request.form.get('action')
            application_id = request.form.get('application_id')

            if action == 'update_status':
                approved_status = request.form.get('approved_status')
                try:
                    sql_update = "UPDATE club_activity_applications SET approved = %s WHERE application_id = %s;"
                    cursor.execute(sql_update, (approved_status, application_id))
                    db.commit()
                    message = '成功更新审批状态'
                except Exception as e:
                    db.rollback()
                    message = f'更新审批状态失败: {e}'

            elif action == 'delete_application':
                try:
                    sql_delete = "DELETE FROM club_activity_applications WHERE application_id = %s;"
                    cursor.execute(sql_delete, (application_id,))
                    db.commit()
                    message = '成功删除活动申请'
                except Exception as e:
                    db.rollback()
                    message = f'删除活动申请失败: {e}'

            # 重新查询所有活动申请
            sql_select = "SELECT * FROM club_activity_applications;"
            cursor.execute(sql_select)
            activities = cursor.fetchall()
            return render_template('admin_page_ActivityApproval.html', user=session.get('user')['name'], user_power=user_power, activities=activities, message=message)

        else:
            # GET 请求时，查询所有活动申请
            sql_select = "SELECT * FROM club_activity_applications;"
            cursor.execute(sql_select)
            activities = cursor.fetchall()
            return render_template('admin_page_ActivityApproval.html', user=session.get('user')['name'], user_power=user_power, activities=activities, message='')

    else:
        return redirect(url_for('login'))  # 未登录或权限不足，重定向到登录页面

@app.route("/admin_page_ClubManagement", methods=["GET", "POST"])
def admin_page_club_management():
    # 仅允许权限2的用户访问
    if session.get('login') == 'OK' and session.get('user')['power'] == 2:
        user_power = session.get('user')['power']  # 获取用户的权限，并传递给前端

        # 获取所有社团信息的函数
        def get_clubs():
            sql = "SELECT * FROM clubs;"
            cursor.execute(sql)
            return cursor.fetchall()

        # 获取社团成员人数的函数
        def get_club_member_count(club_id):
            sql = "SELECT COUNT(*) FROM students WHERE student_club = %s;"
            cursor.execute(sql, (club_id,))
            return cursor.fetchone()[0]

        if request.method == 'POST':
            selected_action = request.form.get('selected_one')

            club_id = request.form.get('club_id')
            club_name = request.form.get('club_name')
            club_advisor = request.form.get('club_advisor')

            if selected_action == '修改社团信息':
                if get_club_member_count(club_id) == 0:
                    # 更新社团信息
                    try:
                        sql_update = "UPDATE clubs SET club_name = %s, club_advisor = %s WHERE club_id = %s;"
                        cursor.execute(sql_update, (club_name, club_advisor, club_id))
                        db.commit()
                        insert_result = '成功修改社团信息'
                    except Exception as e:
                        print(e)
                        db.rollback()
                        insert_result = '修改社团信息失败，请重试'
                else:
                    insert_result = '该社团还有学生，无法修改社团信息'

            elif selected_action == '删除社团信息':
                if get_club_member_count(club_id) == 0:
                    # 删除社团信息
                    try:
                        sql_delete = "DELETE FROM clubs WHERE club_id = %s;"
                        cursor.execute(sql_delete, (club_id,))
                        db.commit()
                        insert_result = '成功删除社团信息'
                    except Exception as e:
                        print(e)
                        db.rollback()
                        insert_result = '删除社团信息失败，请重试'
                else:
                    insert_result = '该社团还有学生，无法删除社团信息'

            # 获取最新的社团列表
            results = get_clubs()
            return render_template('admin_page_ClubManagement.html', user=session.get('user')['name'], user_power=user_power, results=results, insert_result=insert_result)

        else:
            # GET 请求时，获取社团列表并渲染页面
            results = get_clubs()
            return render_template('admin_page_ClubManagement.html', user=session.get('user')['name'], user_power=user_power, results=results)

    else:
        return redirect(url_for('login'))  # 未登录或权限不足，重定向到登录页面

# 启动服务器
if __name__ == '__main__':
    app.debug = True
    try:
        app.run()
    except Exception as err:
        print(err)
        db.close()  # 关闭数据库连接
