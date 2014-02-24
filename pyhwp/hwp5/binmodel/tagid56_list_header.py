# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2014 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from hwp5.binmodel._shared import RecordModelType
from hwp5.binmodel._shared import RecordModel
from hwp5.tagids import HWPTAG_LIST_HEADER
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import SHWPUNIT
from hwp5.dataio import HWPUNIT
from hwp5.dataio import HWPUNIT16
from hwp5.dataio import BYTE
from hwp5.binmodel._shared import Margin
from hwp5.binmodel.controls.table_control import TableControl
from hwp5.binmodel.controls.header_footer import Header
from hwp5.binmodel.controls.header_footer import Footer
from hwp5.binmodel.tagid60_shape_component import ShapeComponent


list_header_models = dict()


class ListHeaderType(RecordModelType):

    def __new__(mcs, name, bases, attrs):
        cls = RecordModelType.__new__(mcs, name, bases, attrs)
        if 'parent_model_type' in attrs:
            parent_model_type = attrs['parent_model_type']
            before_tablebody = attrs.get('before_tablebody', False)
            list_type_key = parent_model_type, before_tablebody
            assert list_type_key not in list_header_models
            list_header_models[list_type_key] = cls
        return cls


class ListHeader(RecordModel):
    __metaclass__ = ListHeaderType
    tagid = HWPTAG_LIST_HEADER

    VAlign = Enum(TOP=0, MIDDLE=1, BOTTOM=2)
    Flags = Flags(UINT32,
                  0, 2, 'textdirection',
                  3, 4, 'linebreak',
                  5, 6, VAlign, 'valign')

    def attributes(cls):
        yield UINT16, 'paragraphs',
        yield UINT16, 'unknown1',
        yield cls.Flags, 'listflags',
    attributes = classmethod(attributes)

    extension_types = list_header_models

    def get_extension_key(context, model):
        ''' (parent model type, after TableBody) '''
        if 'parent' in context:
            context, model = context['parent']
            seen_table_body = context.get('seen_table_body', False)
            return model['type'], seen_table_body
    get_extension_key = staticmethod(get_extension_key)


class TableCaption(ListHeader):
    parent_model_type = TableControl
    before_tablebody = False

    Position = Enum(LEFT=0, RIGHT=1, TOP=2, BOTTOM=3)
    Flags = Flags(UINT32,
                  0, 1, Position, 'position',
                  2, 'include_margin')

    def attributes(cls):
        yield cls.Flags, 'flags',
        yield HWPUNIT, 'width',
        yield HWPUNIT16, 'separation',  # 캡션과 틀 사이 간격
        yield HWPUNIT, 'maxsize',
    attributes = classmethod(attributes)


class TableCell(ListHeader):
    parent_model_type = TableControl
    before_tablebody = True

    def attributes():
        yield UINT16, 'col',
        yield UINT16, 'row',
        yield UINT16, 'colspan',
        yield UINT16, 'rowspan',
        yield SHWPUNIT, 'width',
        yield SHWPUNIT, 'height',
        yield Margin, 'padding',
        yield UINT16, 'borderfill_id',
        yield SHWPUNIT, 'unknown_width',
    attributes = staticmethod(attributes)


class TextboxParagraphList(ListHeader):
    parent_model_type = ShapeComponent

    def attributes():
        yield Margin, 'padding'
        yield HWPUNIT, 'maxwidth'
    attributes = staticmethod(attributes)


class HeaderFooterParagraphList(ListHeader):
    def attributes():
        yield HWPUNIT, 'width'
        yield HWPUNIT, 'height'
        yield BYTE, 'textrefsbitmap'
        yield BYTE, 'numberrefsbitmap'
    attributes = staticmethod(attributes)


class HeaderParagraphList(HeaderFooterParagraphList):
    parent_model_type = Header


class FooterParagraphList(HeaderFooterParagraphList):
    parent_model_type = Footer