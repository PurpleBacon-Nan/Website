from django import forms
from .models import FishStock,Space,MoneyStock

class AddUnitsForm(forms.Form):
    fish = forms.ModelChoiceField(queryset=FishStock.objects.all(), empty_label="Select Fish", label="Choose Fish",widget=forms.Select(attrs={'id': 'custom_fish_id'}))
    quantity = forms.IntegerField(min_value=1, required=True, label="Quantity to Add",widget=forms.NumberInput(attrs={'id': 'id_quantity'}))

    def __init__(self, *args, **kwargs):
        space = kwargs.pop('space', None)
        super().__init__(*args, **kwargs)

        if space:
            self.fields['fish'].queryset = FishStock.objects.filter(space=space)


class RemoveUnitsForm(forms.Form):
    fish = forms.ModelChoiceField(queryset=FishStock.objects.all(), empty_label="Select Fish", label="Choose Fish",widget=forms.Select(attrs={'id': 'custom_fish_id'}))
    quantity = forms.IntegerField(min_value=1, required=True, label="Quantity to Remove",widget=forms.NumberInput(attrs={'id': 'id_quantity'}))

    def __init__(self, *args, **kwargs):
        space = kwargs.pop('space', None)
        super().__init__(*args, **kwargs)

        if space:
            self.fields['fish'].queryset = FishStock.objects.filter(space=space)


class AddFishForm(forms.ModelForm):
    class Meta:
        model = FishStock
        fields = ['name', 'quantity', 'price_per_unit', 'space']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Quantity'}),
            'space': forms.Select(attrs={'class': 'form-control'}),
        }


class DeleteFishForm(forms.Form):
    fish = forms.ModelChoiceField(
        queryset=FishStock.objects.all(),
        empty_label="Select Fish to Remove",
        label="Choose Fish",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class AddMoney(forms.Form):
    balance = forms.DecimalField(
        min_value=0.01,
        required=True,
        label="Amount to add",
        widget=forms.NumberInput(attrs={'id' : 'id_balance' , 'class' : 'form-control' , 'placeholder' : 'Enter Amount'}),)

class RemoveMoney(forms.Form):
    balance = forms.DecimalField(
        min_value=0.01,
        required=True,
        label="Amount to remove",
        widget=forms.NumberInput(attrs={'id' : 'id_balance' , 'class' : 'form-control' , 'placeholder' : 'Enter Amount'}),)

class SpaceForm(forms.ModelForm):
    class Meta:
        model = Space
        fields = ['name']


