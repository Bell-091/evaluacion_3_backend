from django import forms
from django.contrib.auth.models import User
from .models import Maquinaria, TipoFaena, PerfilUsuario

# ------------------------------------------------------------------------------
# 1. FORMULARIO MODELFORM PARA GESTIÓN DE MAQUINARIA (CRUD)
# ------------------------------------------------------------------------------
class MaquinariaForm(forms.ModelForm):
    class Meta:
        model = Maquinaria
        fields = [
            'codigo', 'nombre', 'marca', 'modelo', 'tipo_faena',
            'potencia_hp', 'tarifa_diaria', 'garantia', 'unidades_disponibles',
            'estado', 'imagen', 'descripcion', 'activo'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: RET-101'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Excavadora Hidráulica'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Caterpillar'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 320D'}),
            'tipo_faena': forms.Select(attrs={'class': 'form-select'}),
            'potencia_hp': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'tarifa_diaria': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1000'}),
            'garantia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1000'}),
            'unidades_disponibles': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # Validación clean_ para código único en mayúsculas y sin espacios vacíos
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo', '').strip().upper()
        if len(codigo) < 3:
            raise forms.ValidationError("El código de inventario debe contener al menos 3 caracteres alfanuméricos.")

        # Verificar unicidad al crear nuevo registro (excluyendo la propia instancia al editar)
        qs = Maquinaria.objects.filter(codigo=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"El código '{codigo}' ya está asignado a otro equipo.")
        return codigo

    # Validación clean_ para tarifa diaria no negativa
    def clean_tarifa_diaria(self):
        tarifa = self.cleaned_data.get('tarifa_diaria')
        if tarifa is not None and tarifa < 0:
            raise forms.ValidationError("La tarifa diaria no puede ser un valor negativo.")
        return tarifa

    # Validación clean_ para fianza de garantía no negativa
    def clean_garantia(self):
        garantia = self.cleaned_data.get('garantia')
        if garantia is not None and garantia < 0:
            raise forms.ValidationError("La garantía debe ser un valor mayor o igual a cero.")
        return garantia


# ------------------------------------------------------------------------------
# 2. FORMULARIO DE REGISTRO DE USUARIOS CON PERFIL INTEGRADO
# ------------------------------------------------------------------------------
class RegistroUsuarioForm(forms.ModelForm):
    rut = forms.CharField(
        max_length=12, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'})
    )
    telefono = forms.CharField(
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56 9 1234 5678'})
    )
    empresa = forms.CharField(
        max_length=120, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de su Constructora'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña segura'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita la contraseña'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@empresa.cl'}),
        }

    def clean_confirm_password(self):
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return p2

    def clean_rut(self):
        rut = self.cleaned_data.get('rut', '').strip().upper()
        if len(rut) < 8:
            raise forms.ValidationError("Ingrese un formato de RUT válido.")
        if PerfilUsuario.objects.filter(rut=rut).exists():
            raise forms.ValidationError("Este RUT ya se encuentra registrado.")
        return rut

