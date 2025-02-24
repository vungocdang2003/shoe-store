import math
import random
import string
from datetime import datetime
from  flask import redirect, render_template, request, session, jsonify, url_for, flash
from  flask_login import logout_user, login_user, current_user, login_required
from  app import app, login, dao, utils, oauth
from app.models import LoaiTaiKhoan



@app.route("/")
def TrangChu():
    kw = request.args.get('kw')
    TheloaiID = request.args.get('TheLoai')
    Trang = request.args.get('Trang',1, type=int)
    GiaCa = request.args.get('Gia')
    DatHang = request.args.get('DatHang')
    if DatHang == 'manual':
        DatHang = None
    GiaNhoNhat = None
    GiaLonNhat = None
    if GiaCa:
        Gia = GiaCa.split(':')
        GiaNhoNhat = int(Gia[0])
        GiaLonNhat = int(Gia[1])
        if GiaLonNhat == 'max':
            GiaLonNhat = None
        else:
            GiaLonNhat = int(GiaLonNhat)
    SanPhams = {}
    DoLonTrang =app.config['PAGE_SIZE']
    if Trang is None:
        Trang = 1
    if kw:
        SanPham = dao.Lay_SP(kw = kw, TheLoaiID = TheloaiID, Trang = Trang, GiaNhoNhat = GiaNhoNhat, GiaLonNhat = GiaLonNhat, DatHang = DatHang)
        So = len(dao.Lay_SP(kw, TheloaiID, GiaNhoNhat, GiaLonNhat))
        return  render_template('timkiem.html', SanPham = SanPham, Trangs = math.ceil(So/DoLonTrang), Trang = Trang, kw = kw, GiaCa = GiaCa, DatHang = DatHang)
    if TheloaiID is None:
        theloai = dao.Lay_TheLoai()
        for t in theloai:
            SanPham = dao.Lay_SP(kw , t.Ma, Trang, 4)
            SanPhams[t.Ma] = []
            for s in SanPham:
                SanPhams[t.Ma].append({
                    "MaSP": s.MaSP,
                    "TenSanPham": s.TenSP,
                    "Gia": s.Gia,
                    "AnhBia": s.Anh,
                    "SoLuongTonKho": s.SLTonKho
                })
        return render_template('index.html', SanPham = SanPhams)
    SanPham = dao.Lay_SP(kw = kw, TheloaiID = TheloaiID, Trang = Trang, GiaNhoNhat = GiaNhoNhat, GiaLonNhat = GiaLonNhat, DatHang = DatHang)
    print(SanPham)
    SanPhams = {}
    SanPhams[TheloaiID] = []
    for s in SanPham:
        SanPhams[TheloaiID].append({
            "MaSP": s.MaSP,
            "TenSanPham": s.TenSP,
            "Gia": s.Gia,
            "AnhBia": s.Anh,
            "SLTonKho": s.SLTonKho
        })
    theloai = dao.Lay_TheLoai(TheloaiID)
    So = len(dao.Lay_SP(kw = None, TheloaiID = TheloaiID, GiaNhoNhat = GiaNhoNhat, GiaLonNhat = GiaLonNhat, DatHang = DatHang))
    return  render_template('theloai.html',sanpham = SanPhams, theloai = theloai, Trangs = math.ceil(So/DoLonTrang),Trang = Trang, GiaCa = GiaCa, DatHang = DatHang)


@app.route('/admin/login', methods=['POST'])
def DangNhap_Admin():
    TenDangNhap = request.form.get('TenDangNhap')
    MatKhau = request.form.get('MatKhau')

    user = dao.DangNhap(TenDangNhap=TenDangNhap, MatKhau=MatKhau, LoaiTaiKhoan=LoaiTaiKhoan.ADMIN, Email=None)

    if isinstance(user, str):  # Kiểm tra nếu user là một thông điệp lỗi
        return render_template('dangnhap.html', msg=user)

    login_user(user)  # Đăng nhập người dùng
    session['LoaiTK'] = "ADMIN"
    session['HoTen'] = user.HoTen  # Lưu tên vào phiên

    return redirect('/admin')



@app.route('/dangnhap', methods =['get','post'])
def DangNhap():
    msg = request.args.get('msg', '')

    if request.method == "GET":
        return render_template('dangnhap.html', msg=msg)

    if request.method == "POST":
        Email = request.form.get('Email')
        MatKhau = request.form.get('MatKhau')
        TrangKeTiep = request.args.get('next')

        user = dao.DangNhap(TenDangNhap=None, MatKhau=MatKhau, LoaiTaiKhoan=LoaiTaiKhoan.KHACHHANG, Email=Email)

        if isinstance(user, str):  # Kiểm tra nếu user là một thông điệp lỗi
            return render_template('dangnhap.html', msg=user)
        login_user(user)  # Đăng nhập người dùng
        session['LoaiTK'] = "KHACHHANG"
        session['HoTen'] = user.HoTen  # Lưu tên vào phiên

        if TrangKeTiep:
            return redirect(TrangKeTiep)
        return redirect('/')

@app.route('/login/google/authorize')
def DangNhapGG():
    try:
        google = oauth.create_client('google')
        khoa = google.authorize_access_token()
        thongtin = google.get('userinfo').json()
        email = thongtin['email']
        nguoidung = dao.Lay_TK_KH_Theo_Email(email)
        if not nguoidung:
            print('Hello')
            ten = thongtin['HoTen']
            ma = thongtin['MaTK']
            hash_tag = dao.Lay_SLTK_KhachHang() + 1
            tendangnhap = "#" + str(hash_tag) + " " + ten
            matkhau = ma[3:8]
            dao.Them_TK_KH(ten = ten, email = email, tendangnhap = tendangnhap, matkhau = matkhau)
            nguoidung = dao.Lay_TK_KH_Theo_Email(email)
            login_user(nguoidung = nguoidung)
        else:
            print("Hello")
            login_user(nguoidung = nguoidung)
            session['LoaiTK'] = "KHACHHANG"
    except Exception as error:
        print(error)
    return redirect(url_for('trangchu'))


@app.route('/dangxuat')
def DangXuat():
    logout_user()
    del session['LoaiTK']
    return redirect('/')


@app.route('/nhanvien/logout')
def DangXuatNV():
    logout_user()
    del session['LoaiTK']
    if "giosanpham" in session:
        del session['giosanpham']
    return redirect('/nhanvien')


@app.route('/dangky', methods = ['get','post'])
def DangKy():
    if request.method == "GET":
        return render_template('dangky.html')
    if request.method == "POST":
        HoTen = request.form.get('HoTen')
        Email = request.form.get('Email')
        TenDangNhap = request.form.get('TenDangNhap')
        MatKhau = request.form.get('MatKhau')
        msg = dao.Check_TK(Email, TenDangNhap)
        if msg:
            return render_template('dangky.html', msg = msg)
        session['HoTen'] = HoTen
        session['Email'] = Email
        session['TenDangNhap'] = TenDangNhap
        session['MatKhau'] = MatKhau
        dao.Them_TK_KH(HoTen, Email, TenDangNhap, MatKhau)
        return redirect(url_for('DangNhap', msg="Tài khoản đã được dăng ký thành công!"))


@app.route('/quenmatkhau', methods = (['get', 'post']))
def QuenMatKhau():
    msg = request.args.get('msg')
    if request.method == 'POST':
        Email = request.form.get('Email')
        KiemTra = dao.Lay_TK_KH_Theo_Email(Email)
        if not KiemTra:
            return redirect(url_for('QuenMatKhau', msg = 'Tai Khoan Khong Ton Tai!'))
        session['Email'] = Email
        return redirect(url_for('DangNhap', next = '/quenmatkhau'))
    DoiMatKhau = False
    if 'DoiMatKhau' in session and session['DoiMatKhau'] is True:
        DoiMatKhau = True
    return render_template('quenmatkhau.html', DoiMatKhau = DoiMatKhau, msg = msg)


@app.route('/doimatkhau', methods = ['post'])
def DoiMatKhau():
    MatKhau = request.form.get('MatKhau')
    Email = session['Email']
    dao.Doi_MK_KH(Email, MatKhau)
    del session['doimatkhau']
    return redirect(url_for("Dang nhap", msg = "Mat khau duoc thay doi thanh cong"))


@app.route("/api/cart", methods = ['post'])
def ThemSPVaoGioHang():
    data = request.json
    MaSP = str(data.get("MaSP"))
    SoLuong = int(data.get("SoLuong"))
    MaKH = current_user.MaKH
    dao.Them_GioHang(MaKH, MaSP, SoLuong)
    """
            {
                "1": {
                    "MaSP": "1",
                    "TenSP": "...",
                    "Gia": 123,
                    "SoLuong": 2
                },  "2": {
                    "MaSP": "2",
                    "TenSP": "...",
                    "Gia": 1234,
                    "SoLuong": 1
                }
            }
        """
    return jsonify(dao.Lay_Tong_GioHang(current_user.MaKH))


@app.route("/api/cart/<product_id>", methods = ['put'])
def UpdateGioHang(product_id):
    cart = dao.Lay_GioHang(current_user.MaTK)
    if cart and product_id in cart:
        SoLuong = request.json.get('SoLuong')
        dao.CapNhat_GioHang(current_user.MaKH, product_id, SoLuong)
    return jsonify(dao.Lay_Tong_GioHang(current_user.MaTK))


@app.route("/api/cart/<product_id>", methods = ['delete'])
def XoaGioHang(product_id):
    cart = dao.Lay_GioHang(current_user.MaTK)
    if cart and product_id in cart:
        dao.Xoa_SP_Trong_GioHang(current_user.MaKH, product_id)
    return jsonify(dao.Lay_Tong_GioHang(current_user.MaTK))


@app.route('/giohang')
def GioHang():
    if current_user.LoaiTK == LoaiTaiKhoan.KHACHHANG:
        GioHang = dao.Lay_GioHang(current_user.MaTK)
        msg = request.args.get('msg')
        SLTonKho = {}
        for g in GioHang.values():
            sanpham = dao.Lay_MaSP(g['MaSP'])
            SLTonKho[g['MaSP']] = sanpham.SLTonKho
        return render_template("giohang.html", GioHang = GioHang, msg = msg, SLTonKho = SLTonKho)
    else:
        return ("Co loi xay ra!")


@app.route('/sanpham/<sanpham_id>')
def ChiTietSP(sanpham_id):
    trang = request.args.get('trang')
    dolontrang = 5
    if trang:
        trang = int(trang)
    else:
        trang = 1
    sanpham = dao.Lay_MaSP(sanpham_id)
    theloai = dao.Lay_TheLoaiSP_Theo_MaSP(sanpham_id)
    binhluan = dao.Lay_BinhLuan(sanpham_id, trang = trang, dolontrang = dolontrang)
    num = len(dao.Lay_BinhLuan(sanpham_id))
    soluongdaban = dao.Lay_SL_DaBan(sanpham_id)
    return render_template('chitietsanpham.html', sanpham = sanpham, theloai = theloai,
                           binhluan = binhluan, trangs = math.ceil(num / dolontrang), trang = trang, soluongbinhluan = num, soluongdaban = soluongdaban)


@app.route('/api/binhluan', methods = ['post'])
@login_required
def ThemBinhLuan():
    data = request.json
    MaSP = str(data.get("MaSP"))
    MaKH = current_user.MaTK
    binhluan = str(data.get("binhluan"))
    check = dao.KiemTra_BinhLuan(MaSP, MaKH)
    if check is True:
        dao.Them_BinhLuan(MaSP, MaKH, binhluan)
    return jsonify(check)


@app.route('/nhanvien', methods = ['GET'])
def NhanVien():
    msg = request.args.get('msg', '')  # Đặt giá trị mặc định là ''
    kw = request.args.get('kw', '')  # Đặt giá trị mặc định là ''
    Trang = request.args.get('Trang', 1)  # Đặt giá trị mặc định là 1

    try:
        trang = int(Trang)  # Chuyển đổi Trang thành số nguyên
    except ValueError:
        trang = 1  # Nếu không chuyển đổi được, mặc định về 1

    # Lấy danh sách sản phẩm
    sanpham = dao.Lay_SP(kw=kw, Trang=trang, DoLonTrang=1)

    # Lấy tổng số sản phẩm để tính số trang
    total_products = dao.Lay_SP(kw=kw)
    trangs = len(total_products)  # Sử dụng tổng số sản phẩm để xác định số trang

    giosanpham = session.get("giosanpham")  # Lấy giỏ hàng từ session nếu có

    return render_template('nhanvien.html',
                           sanpham=sanpham,
                           giosanpham=giosanpham,
                           tonggiosp=utils.Dem_Gio_SP(giosanpham),
                           Trang=trang,
                           kw=kw,
                           trangs=trangs,
                           msg=msg)

@app.route('/api/giosanpham', methods = ['post'])
def ThemGioSP():
    data = request.json
    giosanpham = session.get('giosanpham')
    if giosanpham is None:
        giosanpham = {}
    MaSP = str(data.get('ma'))
    if MaSP in giosanpham:
        giosanpham[MaSP]['soluong'] += 1
    else:
        giosanpham[MaSP] = {
            "MaSP": MaSP,
            "TenSP": data.get("TenSP"),
            "Gia": data.get("Gia"),
            "SoLuong": 1
        }
    session['giosanpham'] = giosanpham
    return jsonify(utils.Dem_Gio_SP(giosanpham))


@app.route("/api/giosanpham/<product_id>", methods = ['put'])
def CapNhatGioSP(product_id):
    giosanpham = session.get('giosanpham')
    if giosanpham and product_id in giosanpham:
        SoLuong = request.json.get('SoLuong')
        giosanpham[product_id]['SoLuong'] = int(SoLuong)
    session['giosanpham'] = giosanpham
    return jsonify(utils.Dem_Gio_SP(giosanpham))


@app.route("/api/giosanpham/<product_id>", methods = ['delete'])
def XoaGioSP(product_id):
    giosanpham = session.get('giosanpham')
    if giosanpham and product_id in giosanpham:
        del giosanpham[product_id]
    session['giosanpham'] = giosanpham
    return jsonify(utils.Dem_Gio_SP(giosanpham))


@login.user_loader
def LayNguoiDung(user_id):
    loainguoidung = session.get('LoaiTK')
    if loainguoidung == "ADMIN" or loainguoidung == "NHANVIEN":
        return dao.Lay_TK_NV_theo_ID(user_id)
    elif loainguoidung == "KHACHHANG":
        return dao.Lay_TK_KH_Theo_ID(user_id)


@app.context_processor
def LayTheLoai():
    if current_user.is_authenticated:
        return {
            'TheLoai': dao.Lay_TheLoai(),
            'GioHang': dao.Lay_Tong_GioHang(current_user.MaTK)
        }
    return {
        'TheLoai': dao.Lay_TheLoai()
    }


@app.route('/nhanvien/login', methods=['POST','GET'])
def DangNhapNV():
    TenDangNhap = request.form.get('TenDangNhap', '')  # Đặt giá trị mặc định là ''
    MatKhau = request.form.get('MatKhau', '')  # Đặt giá trị mặc định là ''

    # Kiểm tra nếu tên đăng nhập hoặc mật khẩu trống
    if not TenDangNhap or not MatKhau:
        flash("Tên đăng nhập và mật khẩu không được để trống.")
        return redirect('/nhanvien/login')  # Quay lại trang đăng nhập


    user = dao.DangNhap(TenDangNhap=TenDangNhap, MatKhau=MatKhau, LoaiTaiKhoan=LoaiTaiKhoan.NHANVIEN, Email=None)
    if user is None or isinstance(user, str):  # Kiểm tra nếu NguoiDung là thông điệp lỗi
        flash(user)  # Hiển thị thông điệp lỗi
        return redirect('/nhanvien/login')  # Quay lại trang đăng nhập
    else:
        # Nếu không có lỗi, thực hiện đăng nhập
        login_user(user)
        session['LoaiTK'] = "NHANVIEN"
        session['HoTen'] = user.HoTen  # Lưu tên vào phiên
        return redirect('/nhanvien')  # Chuyển hướng đến trang chính của nhân viên


@app.route('/nhanvien', methods = ['post'])
@login_required
def LapHoaDon():
    giohang = session.get('giosanpham')
    for g in giohang.values():
        kiemtra = dao.KiemTra_TonKho(g['MaSP'], g['SoLuong'])
        if kiemtra is False:
            msg = "Co loi xay ra. San pham " + str(g['TenSP']) + "khong du hang ton kho"
            return redirect(url_for("nhanvien", msg = msg))
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 3))
    MaHD = str(current_user.MaNV) + random_string
    NhanVien = dao.Lay_TK_NV_theo_ID(current_user.MaNV)
    dao.Lap_HoaDon(MaHD = MaHD, MaTK_NV = current_user.MaNV)
    session['MaHD'] = MaHD
    return redirect('/hoadon')


@app.route('/hoadon')
def HoaDon():
    referrer = request.referrer
    if referrer and 'nhanvien' in referrer:
        hoadon = None
        sanphams = None
        if 'MaHD' in session and session['MaHD']:
            MaHD = session.get('MaHD')
            del session['MaHD']
            hoadon = dao.Lay_MaHD(MaHD)
            chitiethoadon = dao.Lay_ChiTietHD_Theo_ID(MaHD)
            sanphams = {}
            for g in chitiethoadon:
                sanpham = dao.Lay_MaSP(g.MaSP)
                sanphams[g.id] = {
                    "MaSP": g.MaSP,
                    "TenSP": sanpham.TenSP,
                    "Gia": sanpham.Gia,
                    "SoLuong": g.SoLuong
                }
        return render_template("hoadon.html", hoadon = hoadon, chitiethoadon = sanphams)
    else:
        return "Co loi xay ra"


if __name__ =='__main__':
    from app import admin
    app.run(host='localhost', port=5000, debug=True)