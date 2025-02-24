def Dem_Gio_SP(giohang):
    TongTien = 0
    TongSoLuong = 0
    if giohang:
        for g in giohang.values():
            TongTien += g['SoLuong'] * g['Gia']
            TongSoLuong += g['SoLuong']
    return {
        "Tong So Luong": TongSoLuong,
        "Tong Tien": TongTien
    }