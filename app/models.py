import hashlib
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from app import db, app
from flask_login import UserMixin
import enum


class BaseModel(db.Model):
    __abstract__ = True
    Ma = Column(Integer, primary_key=True, autoincrement=True)
    NgayKhoiTao = Column(DateTime, default=datetime.utcnow)  # Sửa: sử dụng datetime.utcnow


class LoaiTaiKhoan(enum.Enum):
    ADMIN = 1
    NHANVIEN = 2
    KHACHHANG = 3


class GioiTinh(enum.Enum):
    Nam = 0
    Nu = 1


class TaiKhoan(db.Model, UserMixin):
    __abstract__ = True
    HoTen = Column(String(100), nullable=False)
    TenDangNhap = Column(String(30), nullable=False, unique=True)
    MatKhau = Column(String(100), nullable=False)
    AnhDaiDien = Column(String(200), default='https://www.example.com/default_avatar.png')  # Sửa URL
    LoaiTK = Column(Enum(LoaiTaiKhoan))

    def __str__(self):
        return self.TenDangNhap

    def get_id(self):
        return str(self.MaTK)  # Trả về ID người dùng


class TaiKhoanKhachHang(TaiKhoan):
    MaTK = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Email = Column(String(100), unique=True, nullable=False)
    GioHang = relationship("GioHang", back_populates="TaiKhoanKH", uselist=False)
    BinhLuan = relationship("BinhLuan", backref="taikhoankhachhang2", lazy=True)

    def __str__(self):
        return self.HoTen


class DiaChi(BaseModel):
    diachi = Column(String(100), nullable=False)
    TaiKhoanKH_ID = Column(Integer, ForeignKey(TaiKhoanKhachHang.MaTK), nullable=False)
    TaiKhoanKH = relationship("TaiKhoanKhachHang", backref="diachi", lazy=True)
    HoaDon = relationship("HoaDon", backref="diachi", lazy=True)


class SDT(BaseModel):
    sdt = Column(String(12), nullable=False)
    TaiKhoanKH_ID = Column(Integer, ForeignKey(TaiKhoanKhachHang.MaTK), nullable=False)
    TaiKhoanKH = relationship("TaiKhoanKhachHang", backref="sdt")
    HoaDon = relationship("HoaDon", backref="sdt", lazy=True)


class GioHang(db.Model):
    Ma = Column(Integer, ForeignKey(TaiKhoanKhachHang.MaTK), primary_key=True, nullable=False)
    TaiKhoanKH = relationship("TaiKhoanKhachHang", back_populates="GioHang", uselist=False)
    NgayKhoiTao = Column(DateTime, default=datetime.utcnow)  # Sửa


class NhanVien(BaseModel):
    MaNV = Column(String(20), nullable=False, unique=True)
    HoTen = Column(String(50), nullable=False)
    GioiTinh = Column(Enum(GioiTinh), nullable=False)
    TaiKhoanNV = relationship("TaiKhoanNhanVien", back_populates="NhanVien", uselist=False)

    def __str__(self):
        return self.HoTen


class TaiKhoanNhanVien(TaiKhoan):
    MaTK = Column(Integer, ForeignKey(NhanVien.Ma), primary_key=True, autoincrement=True)  # Sửa ForeignKey
    NhanVien = relationship("NhanVien", back_populates="TaiKhoanNV", uselist=False)

    def __str__(self):
        return self.HoTen


class TheLoai(BaseModel):
    __tablename__ = 'TheLoai'
    # MaTL = Column(Integer, nullable=False, primary_key=True)
    TenTheLoai = Column(String(100), nullable=False, unique=True)

    def __str__(self):
        return self.TenTheLoai


class SanPham(db.Model):
    __tablename__ = 'SanPham'
    MaSP = Column(String(10), primary_key=True, nullable=False)
    TenSP = Column(String(100), nullable=False, unique=True)
    Gia = Column(Float, default=0)
    Size = Column(Float)
    Anh = Column(String(1000))
    SLTonKho = Column(Integer)
    NgaySanXuat = Column(DateTime, default=datetime.utcnow, nullable=False)  # Sửa
    MoTa = Column(String(2000), nullable=False, default='Ko co mo ta')
    BinhLuan = relationship("BinhLuan", backref="sanpham3", lazy=True)

    def __str__(self):
        return self.TenSP


class BinhLuan(BaseModel):
    MaSP = Column(String(10), ForeignKey(SanPham.MaSP), nullable=False)
    MaKH = Column(Integer, ForeignKey(TaiKhoanKhachHang.MaTK), nullable=False)
    NoiDung = Column(String(2000), nullable=False)


class GioHangChuaSanPham(BaseModel):
    MaGH = Column(Integer, ForeignKey(GioHang.Ma), nullable=False)
    MaSP = Column(String(10), ForeignKey(SanPham.MaSP), nullable=False)
    SoLuong = Column(Integer, nullable=False)


class SanPhamThuocTheLoai(BaseModel):
    __tablename__ = 'SanPham_TheLoai'
    MaSP = Column(String(10), ForeignKey(SanPham.MaSP), nullable=False)
    MaTL = Column(Integer, ForeignKey(TheLoai.Ma), nullable=False)
    SanPham = relationship("SanPham", backref="sanpham_theloai1", lazy=True)
    TheLoai = relationship("TheLoai", backref="sanpham_theloai2", lazy=True)


class HoaDon(db.Model):
    MaHD = Column(String(10), primary_key=True, nullable=False)
    TaiKhoanKhachHang_ID = Column(Integer, ForeignKey(TaiKhoanKhachHang.MaTK), nullable=False)
    TaiKhoanNhanVien_ID = Column(Integer, ForeignKey(TaiKhoanNhanVien.MaTK), nullable=False)  # Sửa ForeignKey
    DiaChi_ID = Column(Integer, ForeignKey(DiaChi.Ma), nullable=False)
    SDT_ID = Column(Integer, ForeignKey(SDT.Ma), nullable=False)
    NgayKhoiTao = Column(DateTime, default=datetime.utcnow)  # Sửa
    TaiKhoanKhachHang = relationship("TaiKhoanKhachHang", backref="hoadon1", lazy=True)
    TaiKhoanNhanVien = relationship("TaiKhoanNhanVien", backref="hoadon2", lazy=True)
    __table_args__ = (CheckConstraint('TaiKhoanKhachHang_ID IS NOT NULL or TaiKhoanNhanVien_ID IS NOT NULL'),)
    TongSoLuong = Column(Integer, default=0)
    TongTien = Column(Float, default=0)  # Sửa float thành Float


class ChiTietHoaDon(BaseModel):
    HoaDon_ID = Column(String(10), ForeignKey(HoaDon.MaHD), nullable=False)
    SanPham_ID = Column(String(10), ForeignKey(SanPham.MaSP), nullable=False)
    SoLuong = Column(Integer, nullable=False)


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        # nv1 = NhanVien(MaNV='123', HoTen='Nguyen Van A', GioiTinh=GioiTinh.Nam)
        # db.session.add(nv1)
        # db.session.commit()
        # nv2 = NhanVien(MaNV='456', HoTen='Tran Thi B', GioiTinh=GioiTinh.Nu)
        # db.session.add(nv2)
        # db.session.commit()
        # TK_Admin = TaiKhoanNhanVien(HoTen='Nguyen Van A', TenDangNhap='admin', MatKhau=str(hashlib.md5('123456789'.encode('utf-8')).hexdigest()), LoaiTK=LoaiTaiKhoan.ADMIN)
        # db.session.add(TK_Admin)
        # db.session.commit()
        # TK_NhanVien = TaiKhoanNhanVien(HoTen='Tran Thi B', TenDangNhap='nv1', MatKhau=str(hashlib.md5('123456789'.encode('utf-8')).hexdigest()), LoaiTK=LoaiTaiKhoan.NHANVIEN)
        # db.session.add(TK_NhanVien)
        # db.session.commit
        pass

