from  flask import  session
from  app.models import GioHang, SanPham, TheLoai, SanPhamThuocTheLoai, TaiKhoanKhachHang, TaiKhoanNhanVien, LoaiTaiKhoan, TaiKhoan, \
                        GioHangChuaSanPham, HoaDon, ChiTietHoaDon, BinhLuan, SDT
from app import  app, db, utils
from sqlalchemy import func
import hashlib

def Lay_SP(kw = None, TheLoaiID = None, Trang = None, DoLonTrang = None, GiaLonNhat = None, GiaNhoNhat = None, DatHang =None):
    SanPhams = SanPham.query
    if kw:
        SanPhams = SanPhams.filter(SanPham.TenSP.contains(kw))
    if TheLoaiID:
        SanPhams = SanPhams.filter(SanPham.MaSP.__eq__(SanPhamThuocTheLoai.MaSP)).filter(SanPhamThuocTheLoai.Ma.__eq__(TheLoaiID))
    if GiaLonNhat:
        SanPhams = SanPhams.filter(SanPham.Gia <= GiaLonNhat)
    if GiaNhoNhat:
        SanPhams = SanPhams.filter(SanPham.Gia >= GiaNhoNhat)
    if DatHang and DatHang == 'Ban_Tot_Nhat':
        SanPhams = SanPhams.outerjoin(ChiTietHoaDon, ChiTietHoaDon.SanPham_ID.__eq__(SanPham.MaSP)).group_by(SanPham.MaSP).order_by(func.sum(ChiTietHoaDon.SoLuong).desc())
    elif DatHang == 'TieuDe_Tang':
        SanPhams = SanPhams.order_by(SanPham.TenSP.asc())
    elif DatHang == 'TieuDe_Giam':
        SanPhams = SanPhams.order_by(SanPham.TenSP.desc())
    elif DatHang == 'PhatHanh_Tang':
        SanPhams = SanPhams.order_by(SanPham.NgaySanXuat.asc())
    elif DatHang == 'PhatHanh_Giam':
        SanPhams = SanPhams.order_by(SanPham.NgaySanXuat.desc())
    elif DatHang == 'Gia_Tang':
        SanPhams = SanPhams.order_by(SanPham.Gia.asc())
    elif DatHang == 'Gia_Giam':
        SanPhams = SanPhams.order_by(SanPham.Gia.desc())
    if Trang:
        Trang = int(Trang)
        if DoLonTrang is None:
            DoLonTrang = app.config['Page_Size']
        BatDau = (Trang -1) * DoLonTrang
        SanPhams = SanPhams.slice(BatDau, BatDau + DoLonTrang)
    return SanPhams.all()


def Lay_SoLuongSP():
    return SanPham.query.count()


def Lay_MaSP(MaSP):
    return  SanPham.query.get(MaSP)


def Lay_TheLoaiSP():
    return  SanPhamThuocTheLoai.query.all()


def Lay_SoLuongSP_Theo_TheLoai():
    return db.session.query(TheLoai.Ma, TheLoai.TenTheLoai, func.count(SanPhamThuocTheLoai.MaSP)) \
        .join (SanPhamThuocTheLoai, SanPhamThuocTheLoai.Ma.__eq__(TheLoai.Ma), isouter = True) \
        .group_by(TheLoai.Ma, TheLoai.TenTheLoai).all()


def Lay_TheLoaiSP_Theo_MaSP(MaSP):
    TheLoaiSP = SanPhamThuocTheLoai.query.filter(SanPhamThuocTheLoai.MaSP.__eq__(MaSP)).all()
    TheLoai = []
    for t in  TheLoaiSP:
        TheLoai.append(TheLoai.query.get(t.Ma))
    return TheLoai


def Lay_TK_NV_theo_ID(MaTK):
    return TaiKhoanNhanVien.query.get(MaTK)


def Lay_TK_KH_Theo_ID(MaTK):
    return  TaiKhoanKhachHang.query.get(MaTK)


def Lay_TK_KH_Theo_Email(mail):
    return  TaiKhoanKhachHang.query.filter(TaiKhoanKhachHang.Email.__eq__(mail)).first()


def Lay_SLTK_KhachHang():
    return TaiKhoanKhachHang.query.count()


import hashlib


def DangNhap(TenDangNhap, MatKhau, LoaiTaiKhoan, Email):
    # Kiểm tra nếu TenDangNhap hoặc MatKhau là None
    if MatKhau is None:
        return "mật khẩu không được để trống."

    MatKhau = str(hashlib.md5(MatKhau.strip().encode('utf-8')).hexdigest())

    if LoaiTaiKhoan == LoaiTaiKhoan.ADMIN or LoaiTaiKhoan == LoaiTaiKhoan.NHANVIEN:
        return TaiKhoanNhanVien.query.filter(
            TaiKhoanNhanVien.TenDangNhap.__eq__(TenDangNhap.strip()),
            TaiKhoanNhanVien.MatKhau.__eq__(MatKhau),
            TaiKhoanNhanVien.LoaiTK.__eq__(LoaiTaiKhoan)
        ).first()

    if LoaiTaiKhoan == LoaiTaiKhoan.KHACHHANG:
        taikhoan = TaiKhoanKhachHang.query.filter(
            TaiKhoanKhachHang.Email.__eq__(Email),
            TaiKhoanKhachHang.MatKhau.__eq__(MatKhau)
        ).first()

        if taikhoan:
            return taikhoan
        else:
            return "Tên đăng nhập hoặc mật khẩu sai. Vui lòng nhập lại!"


import hashlib


def Them_TK_KH(HoTen, Email, TenDangNhap, MatKhau):
    # Kiểm tra nếu bất kỳ trường nào cần thiết là None
    if not all([HoTen, Email, TenDangNhap, MatKhau]):
        return "Tất cả các trường đều phải được điền."

    # Tiến hành xử lý khi tất cả các trường hợp lệ
    MatKhau_hash = str(hashlib.md5(MatKhau.strip().encode('utf-8')).hexdigest())

    taikhoan = TaiKhoanKhachHang(
        HoTen=HoTen,
        Email=Email,
        TenDangNhap=TenDangNhap,
        MatKhau=MatKhau_hash,
        AnhDaiDien='https://www.example.com/default_avatar.png',  # Gán ảnh đại diện mặc định
        LoaiTK=LoaiTaiKhoan.KHACHHANG
    )

    giohang = GioHang(TaiKhoanKH=taikhoan)

    db.session.add(taikhoan)
    db.session.commit()
    db.session.add(giohang)
    db.session.commit()


def Doi_MK_KH(Email, MatKhau):
    taikhoan = Lay_TK_KH_Theo_Email(Email)
    taikhoan.MatKhau = str(hashlib.md5(MatKhau.strip().encode('utf-8')).hexdigest())
    db.session.commit()


def Check_TK(Email, TenDangNhap):
    check_email = TaiKhoanKhachHang.query.filter(TaiKhoanKhachHang.Email.__eq__(Email)).all()
    check_tendangnhap = TaiKhoanKhachHang.query.filter(TaiKhoanKhachHang.TenDangNhap.__eq__(TenDangNhap)).all()
    ThongBao = "Tai khoan da ton tai"
    if check_email:
        return ThongBao
    if check_tendangnhap:
        return  ThongBao
    return None


def Lay_TheLoai(Ma = None):
    if Ma:
        return TheLoai.query.get(Ma)
    return TheLoai.query.all()


def Lay_GioHang(ID_KH):
    giohang = GioHangChuaSanPham.query.filter(GioHangChuaSanPham.MaGH.__eq__(ID_KH)).all()
    gioHang = {}
    for g in giohang:
        sanpham = SanPham.query.filter(SanPham.MaSP.__eq__(g.masp)).first()
        gioHang[sanpham.masp] ={
            "MaSP": sanpham.MaSP,
            "TenSP": sanpham.TenSP,
            "Gia": sanpham.Gia,
            "SoLuong": sanpham.SoLuong,
            "AnhBia": sanpham.Anh
        }
    return gioHang


def Lay_Tong_GioHang(ID_KH):
    giohang = GioHangChuaSanPham.query.filter(GioHangChuaSanPham.MaGH.__eq__(ID_KH)).all()
    thanhtien = 0
    tongsoluong = 0
    for g in giohang:
       soluong = g.SoLuong
       sanpham = SanPham.query.filter(SanPham.MaSP.__eq__(g.masp)).first()
       gia = SanPham.Gia
       thanhtien += gia * soluong
       tongsoluong += soluong
    return {
        "Tong_Tien":thanhtien,
        "Tong_SoLuong": tongsoluong
    }


def Them_GioHang(ID_KH, ID_SP, SoLuong = 1):
    giohang = GioHangChuaSanPham.query.filter(GioHangChuaSanPham.MaGH.__eq__(ID_KH)).filter(
        GioHangChuaSanPham.MaSP.__eq__(ID_SP)
    ).first()
    if giohang:
        giohang.SoLuong += SoLuong
        db.session.commit()
    else:
        giohang_sanpham = GioHangChuaSanPham(MaGH = ID_KH, MaSP = ID_SP, SoLuong = SoLuong)
        db.session.add(giohang_sanpham)
        db.session.commit()


def CapNhat_GioHang(ID_KH, ID_SP, SoLuong):
    giohang = GioHangChuaSanPham.query.filter(GioHangChuaSanPham.MaGH.__eq__(ID_KH)).filter(
        GioHangChuaSanPham.MaSP.__eq__(ID_SP)
    ).first()
    giohang.SoLuong = SoLuong
    db.session.commit()


def Xoa_SP_Trong_GioHang(ID_KH, ID_SP):
    giohang = GioHangChuaSanPham.query.filter(GioHangChuaSanPham.MaGH.__eq__(ID_KH)).filter(
        GioHangChuaSanPham.MaSP.__eq__(ID_SP)
    ).first()
    db.session.delete(giohang)
    db.session.commit()


def KiemTra_TonKho(ID_SP, SoLuong):
    sanpham = SanPham.query.get(ID_SP)
    if sanpham.SLTonKho >= SoLuong:
        return True
    return False


def Lap_HoaDon(MaHD, MaTK_KH = None, MaTK_NV = None,DiaChi = None, SDT = None):
    if MaTK_NV != None:
        gioSP = session.get('gioSP')
        giohang = utils.Dem_Gio_SP(gioSP)
        hoadon = HoaDon(MaHD = MaHD, MaTK_NV = MaTK_NV, TongSoLuong = giohang['TongSoLuong'], TongTien = giohang['TongTien'])
        db.session.add(hoadon)
        db.session.commit()
        for g in gioSP.values():
            chitiethoadon = ChiTietHoaDon(MaHD = MaHD, MaSP = g['MaSP'], SoLuong = g['SoLuong'])
            sanpham = SanPham.query.get(g['MaSP'])
            sanpham.SLTonKho -= g['SoLuong']
            db.session.add(chitiethoadon)
            db.session.commit()
        del session['giosanpham']
    if MaTK_KH != None and DiaChi != None and SDT != None:
        giohang = Lay_Tong_GioHang(MaTK_KH)
        kiemtraDC = DiaChi.query.filter(DiaChi.diachi.__eq__(DiaChi)).filter(
            DiaChi.TaiKhoanKH_ID.__eq__(MaTK_KH)
        ).first()
        kiemtraSDT = SDT.query.filter(SDT.sdt.__eq__(SDT)).filter(
            SDT.TaiKhoanKH_ID.__eq__(MaTK_KH)
        ).first()
        if kiemtraDC is None:
            diachi = DiaChi(diachi = DiaChi,MaTK_KH = MaTK_KH)
            db.session.add(diachi)
        else:
            diachi = kiemtraDC
        if kiemtraSDT is None:
            sdt = SDT(sdt = SDT, MaTK_KH = MaTK_KH)
            db.session.add(sdt)
        else:
            sdt = kiemtraSDT
        db.session.commit()

        hoadon = HoaDon(MaHD = MaHD, MaTK_KH = MaTK_KH, DiaChi = DiaChi, SDT = SDT,
                        TongSoLuong = giohang['TongSoLuong'], TongTien = giohang['TongTien'])
        db.session.add(hoadon)
        db.session.commit()
        gioHang = Lay_GioHang(MaTK_KH)
        for g in gioHang.values():
            chitiethoadon = ChiTietHoaDon(MaHD = MaHD, MaSP = g['MaSP'], SoLuong = g['SoLuong'])
            sanpham = SanPham.query.get(g['MaSP'])
            sanpham.SLTonKho -= g['SoLuong']
            db.session.add(chitiethoadon)
            db.session.commit()
        gioHang = GioHangChuaSanPham.query.filter(GioHangChuaSanPham.MaGH.__eq__(MaTK_KH)).all()
        for g in gioHang:
            db.session.delete(g)
        db.session.commit()


def KiemTra_BinhLuan(MaSP, MaKH):
    hoadon = HoaDon.query.filter(HoaDon.TaiKhoanKhachHang_ID.__eq__(MaKH)).all()
    for h in hoadon:
        chitiethoadon = ChiTietHoaDon.query.filter(ChiTietHoaDon.HoaDon_ID.__eq__(h.HoaDon_ID)).filter(
            ChiTietHoaDon.SanPham_ID.__eq__(MaSP)
        )
        if chitiethoadon:
            return True
    return False


def Them_BinhLuan(ID_SP, ID_KH, BinhLuan):
    binhluan = BinhLuan(MaSP = ID_SP, MaTK = ID_KH, NoiDung = BinhLuan)
    db.session.add(binhluan)
    db.session.commit()


def Lay_BinhLuan(ID_SP, Trang = None, DoLonTrang = None):
    binhluan = BinhLuan.query.filter(BinhLuan.MaSP.__eq__(ID_SP))
    if Trang:
        Trang= int(Trang)
        if DoLonTrang is None:
            DoLonTrang = app.config['PAGE_SIZE']
        BatDau =(Trang - 1) * DoLonTrang
        binhluan = binhluan.slice(BatDau, BatDau + DoLonTrang)
    binhluan = binhluan.all()
    binhluan = {}
    for b in binhluan:
        khachhang = TaiKhoanKhachHang.query.get(b.MaTK)
        binhluan[b.id] = {
            "TenKhachHang": khachhang.TenKH,
            "NgayBinhLuan": b.NgayKhoiTao,
            "NoiDung": b.NoiDung
        }
    return binhluan


def Lay_SL_DaBan(ID_SP):
    TraVe =(
        db.session.query(func.sum(ChiTietHoaDon.SoLuong)).filter(ChiTietHoaDon.SanPham_ID == ID_SP).first()
    )
    if TraVe and TraVe[0] is not None:
        TongSoLuong = TraVe[0]
    else:
        TongSoLuong = 0
    return TongSoLuong


def BieuDo_SP(kw = None):
    Chon = db.session.query(SanPham.MaSP, SanPham.TenSP, func.sum(ChiTietHoaDon.SoLuong * SanPham.Gia))\
    .join(ChiTietHoaDon, ChiTietHoaDon.SanPham_ID == SanPham.MaSP)
    if kw:
        Chon = Chon.filter(SanPham.TenSP.contains(kw))
    return Chon.group_by(SanPham.MaSP).all()


def BieuDo_Thang_SP(year = 2024):
    Chon = db.session.query(func.extract('month', HoaDon.NgayKhoiTao),
                            func.sum(ChiTietHoaDon.SoLuong * SanPham.Gia))\
                        .join(ChiTietHoaDon, ChiTietHoaDon.HoaDon_ID.__eq__(HoaDon.MaHD))\
                        .join(SanPham, SanPham.MaSP.__eq__(ChiTietHoaDon.SanPham_ID))\
                        .filter(func.extract('year', HoaDon.NgayKhoiTao).__eq__(year))\
                        .group_by(func.extract('month', HoaDon.NgayKhoiTao))
    return Chon.all()


def BieuDo_Nam_SP():
    Chon = db.session.query(func.extract('year', HoaDon.NgayKhoiTao),
                            func.sum(ChiTietHoaDon.SoLuong * SanPham.Gia))\
                            .join(ChiTietHoaDon, ChiTietHoaDon.HoaDon_ID.__eq__(HoaDon.MaHD))\
                            .join(SanPham, SanPham.MaSP.__eq__(ChiTietHoaDon.SanPham_ID))\
                            .group_by(func.extract('year', HoaDon.NgayKhoiTao))
    return Chon.all()


def Lay_MaHD(MaHD):
    return HoaDon.query.get(MaHD)


def Lay_ChiTietHD_Theo_ID(MaHD):
    return  ChiTietHoaDon.query.filter(ChiTietHoaDon.HoaDon_ID.__eq__(MaHD)).all()


