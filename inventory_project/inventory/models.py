from django.db import models


class Izm(models.Model):
    title = models.CharField("Ед.изм",max_length=50, unique=True,blank=False)

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'izm'
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'


class Category(models.Model):
    title = models.CharField('Категория',max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'category'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Nom(models.Model):
    title = models.CharField('Наименование',max_length=200, blank=False, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        verbose_name='Категория'

    )
    izm = models.ForeignKey(
        Izm,
        on_delete=models.PROTECT,  # Нельзя удалить единицу измерения, если есть товары с ней
        blank=True,
        null=True,
        verbose_name='Ед.изм.'
    )

    def __str__(self):
        return self.title or 'Без названия'

    class Meta:
        managed = False
        db_table = 'nom'
        verbose_name = 'Номенклатура'
        verbose_name_plural = 'Номенклатура'


class Podraz(models.Model):
    title = models.CharField('Подразделение',max_length=100, unique=True,blank=False)

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'podraz'
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'


class Obct(models.Model):
    title = models.CharField('Объект',max_length=100)  # Добавил max_length
    idpodraz = models.ForeignKey(
        Podraz,
        on_delete=models.PROTECT,
        db_column='idpodraz',
        verbose_name='Подразделение'
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'obct'
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'


class Postav(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'postav'
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


class Fio(models.Model):
    title = models.CharField('Подотчетное лицо',max_length=100, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'fio'
        verbose_name = 'Подотчетное лицо'
        verbose_name_plural = 'Подотчетные лица'


class Doc(models.Model):
    nomer = models.CharField('Номер',max_length=50)
    datadoc = models.CharField('Дата',max_length=50)
    postav = models.ForeignKey(Postav, on_delete=models.PROTECT,verbose_name='Поставщик')
    obct = models.ForeignKey(Obct, on_delete=models.SET_NULL, blank=True, null=True,verbose_name='Объект')
    fio = models.ForeignKey(Fio, on_delete=models.PROTECT,verbose_name='Подотчет')
    oper = models.IntegerField('Операция')
    update_date = models.DateTimeField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,verbose_name='Итого')  # Числовое поле

    def __str__(self):
        return f"Документ №{self.nomer} от {self.datadoc}"

    class Meta:
        managed = False
        db_table = 'doc'
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'


class Detail(models.Model):
    id_doc = models.ForeignKey(
        Doc,
        on_delete=models.PROTECT,
        db_column='id_doc',
        blank=True,
        null=True,
        related_name='details'  # Позволит обращаться doc.details.all()
    )
    id_nom = models.ForeignKey(
        Nom,
        on_delete=models.PROTECT,  # Нельзя удалить товар, если он есть в деталях
        db_column='id_nom',
        blank=True,
        null=True,
        verbose_name='Наименование'
    )
    kolvo = models.DecimalField('Количество',max_digits=12, decimal_places=4)  # Количество
    price = models.DecimalField('Цена',max_digits=10, decimal_places=2)  # Цена
    cost = models.DecimalField('Стоимость',max_digits=10, decimal_places=2)  # Стоимость
    oper = models.IntegerField('Тип документа',blank=True, null=True)

    def __str__(self):
        return f"{self.id_nom} - {self.kolvo} x {self.price}"

    class Meta:
        managed = False
        db_table = 'detail'
        verbose_name = 'Табличная часть документа'
        verbose_name_plural = 'Табличная часть документов'


# class Akt(models.Model):
#     nomer = models.IntegerField()
#
#     def __str__(self):
#         return f"Акт №{self.nomer}"
#
#     class Meta:
#         managed = False
#         db_table = 'akt'
#         verbose_name = 'Акт'
#         verbose_name_plural = 'Акты'


class Spis(models.Model):
    title = models.CharField(max_length=100, unique=True,blank=False)

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'spis'
        verbose_name = 'Списание'
        verbose_name_plural = 'Списания'