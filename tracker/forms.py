from django import forms

from .models import Category, Person, Task


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].empty_label = 'Üst kategori yok'
        self.fields['name'].widget.attrs['placeholder'] = 'Örn. Eğitim / Yazılım'
        self.fields['description'].widget.attrs['placeholder'] = 'Kategori hakkında kısa açıklama'

    class Meta:
        model = Category
        fields = ['name', 'parent', 'description', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'role']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }


class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Kategori seçin (opsiyonel)'
        self.fields['responsible'].empty_label = 'Sorumlu seçin'
        self.fields['worker'].empty_label = 'İş alan seçin'
        self.fields['owner_group'].widget.attrs['placeholder'] = 'Örn. Yazılım, Okul işleri, Kişisel'
        self.fields['title'].widget.attrs['placeholder'] = 'Görev başlığını yazın'
        self.fields['details'].widget.attrs['placeholder'] = 'Kısa not, yapılacak adımlar veya açıklama'

    class Meta:
        model = Task
        fields = [
            'plan_date',
            'owner_group',
            'category',
            'responsible',
            'worker',
            'section',
            'title',
            'details',
            'due_date',
            'priority',
            'is_completed',
        ]
        widgets = {
            'plan_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'owner_group': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'responsible': forms.Select(attrs={'class': 'form-select'}),
            'worker': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
