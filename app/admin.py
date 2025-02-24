import hashlib
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from app import app, db, dao
from app.models import SanPham, TheLoai, SanPhamThuocTheLoai, TaiKhoanNhanVien, TaiKhoanKhachHang, NhanVien, LoaiTaiKhoan
from flask_login import logout_user, current_user
from flask import redirect, request


class TrangChu(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats=dao.Lay_SoLuongSP_Theo_TheLoai())


admin = Admin(app=app, name='QUẢN LÝ BÁN GIÀY', template_mode='bootstrap4', index_view=TrangChu())


class XacThucAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.LoaiTK == LoaiTaiKhoan.ADMIN


class XacThucNguoiDung(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and (
            current_user.LoaiTK == LoaiTaiKhoan.NHANVIEN or current_user.LoaiTK == LoaiTaiKhoan.ADMIN
        )


class XacThucAdminCanBan(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.LoaiTK == LoaiTaiKhoan.ADMIN


class XacThucNhanVienCanBan(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.LoaiTK == LoaiTaiKhoan.NHANVIEN


class XemSP(XacThucAdmin):
    column_display_pk = True
    can_create = True
    column_list = ['MaSP', 'TenSP', 'Gia', 'Size', 'SLTonKho', 'sanpham_theloai1']
    column_labels = {
        'MaSP': 'MaSP',
        'TenSP': 'Tên Giày',
        'Gia': 'Giá',
        'Size': 'Size',
        'SLTonKho': 'Số Lượng Tồn Kho',
        'sanpham_theloai1': 'Thể Loại',
        'MoTa': 'Mô Tả',
        'NgaySanXuat': 'Ngày Sản Xuất',
        'Anh': 'Ảnh Bìa'
    }
    can_export = True
    column_searchable_list = ['TenSP']
    column_filters = ['Gia', 'TenSP']
    column_editable_list = ['MaSP', 'TenSP', 'Gia', 'Size', 'Anh', 'SLTonKho']
    details_modal = True
    edit_modal = True
    form_columns = ['MaSP', 'TenSP', 'Gia', 'Size', 'NgaySanXuat', 'MoTa', 'SLTonKho', 'Anh']


class XemTheLoai(XacThucAdmin):
        column_list = ['Ma', 'TenTheLoai', 'NgayKhoiTao']
        column_labels = {
            'Ma': 'Mã Thể Loại',
            'TenTheLoai': 'Tên Thể Loại',
            'NgayKhoiTao': 'Ngày Khởi Tạo'
        }
        can_export = True
        column_searchable_list = ['TenTheLoai']
        column_filters = ['TenTheLoai']
        column_editable_list = ['TenTheLoai']
        form_columns = ['TenTheLoai', 'NgayKhoiTao']
        details_modal = True
        edit_modal = True


class XemTheLoaiCuaSanPham(XacThucAdmin):
    column_list = ['MaSP', 'SanPham', 'TheLoai']
    column_labels = {
        'MaSP': 'Mã Sản Phẩm',
        'Ma': 'Mã Thể Loại'
    }
    can_export = True


class XemNhanVien(XacThucAdmin):
    column_list = ['MaNV', 'HoTen', 'GioiTinh', 'TaiKhoanNV']
    form_columns = ['MaNV', 'HoTen', 'GioiTinh']
    column_labels = {
        'MaNV': 'Mã Nhân Viên',
        'HoTen': 'Họ Tên',
        'GioiTinh': 'Giới Tính',
        'TaiKhoanNV': 'Tài Khoản Nhân Viên'
    }


class XemDangXuat(XacThucAdminCanBan):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


class XemThongKe(XacThucNguoiDung):
    @expose("/")
    def index(self):
        kw = request.args.get('kw')
        year = request.args.get('year')
        if year:
            year = int(year)
        else:
            year = 2024
        return self.render('admin/stats.html',
                           BieuDo=dao.BieuDo_SP(kw=kw),
                           BieuDoThang=dao.BieuDo_Thang_SP(year=year),
                           BieuDoNam=dao.BieuDo_Nam_SP())


class XemTaiKhoanNhanVien(XacThucAdmin):
    form_columns = ['NhanVien', 'HoTen', 'TenDangNhap', 'MatKhau', 'AnhDaiDien', 'LoaiTK']
    column_labels = {
        'NhanVien': 'Nhân Viên',
        'HoTen': 'Họ Tên',
        'TenDangNhap': 'Tên Đăng Nhập',
        'MatKhau': 'Mật Khẩu',
        'AnhDaiDien': 'Ảnh Đại Diện'
    }

    def on_model_change(self, form, model, is_created):
        if 'MatKhau' in request.form and request.form['MatKhau']:
            model.MatKhau = str(hashlib.md5(request.form['MatKhau'].encode('utf-8')).hexdigest())


class XemTraVe(XacThucNhanVienCanBan):
    @expose("/")
    def TraVe(self):
        return redirect('/NhanVien')


# Thêm các view vào admin
admin.add_view(XemSP(SanPham, db.session))  # Thay 'Ten' thành 'name'
admin.add_view(XemTheLoai(TheLoai, db.session))  # Thay 'Ten' thành 'name'
admin.add_view(XemTheLoaiCuaSanPham(SanPhamThuocTheLoai, db.session))  # Thay 'Ten' thành 'name'
admin.add_view(XemTaiKhoanNhanVien(TaiKhoanNhanVien, db.session))  # Thay 'Ten' thành 'name'
admin.add_view(XemNhanVien(NhanVien, db.session))  # Thay 'Ten' thành 'name'
admin.add_view(XemThongKe(name='Báo Cáo Thống Kê'))  # Thay 'Ten' thành 'name'
admin.add_view(XemTraVe(name='Quay Ve'))  # Thay 'Ten' thành 'name'
admin.add_view(XemDangXuat(name='Đăng Xuất'))  # Thay 'Ten' thành 'name'
