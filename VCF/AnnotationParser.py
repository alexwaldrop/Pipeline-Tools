from collections import OrderedDict

from VCFHelper import VCFHelper
from VCFAnnotationType import VCFAnnotationType

class AnnotationParser(object):
    # Class for parsing annotation information from VCF files

    def __init__(self, vcf_parser):

        # Determine annotation type
        self.annotation_type = self.calc_annotation_type(vcf_parser)

        # Get list of info fields that should appear in each VCF record in the correct order
        self.info_fields = VCFHelper.get_info_field_names(vcf_parser)

        if self.annotation_type is VCFAnnotationType.SNPEFF:
            self.snpeff_info_fields = VCFHelper.get_snpeff_ann_field_names(vcf_parser)

    def get_info(self, record):
        # Return a sorted dictionary of annotations associated with a record
        # Guaranteed to have value for all entries declared in VCF header
        # Guaranteed to be in same order as they appear in VCF header
        if self.annotation_type is VCFAnnotationType.SNPEFF:
            # Unpack the snpeff 'ANN' annotation field into the record info
            self.__unpack_snpeff_info(record)

        # Put data in correct order
        info_data = OrderedDict()

        for info_field in self.info_fields:
            # Get data if present in current info, set to 'None' otherwise
            info_data[info_field] = None if info_field not in record.INFO else record.INFO[info_field]
            # Remove from list if data is list
            if isinstance(info_data[info_field], list):
                info_data[info_field] = info_data[info_field][0]
        return info_data

    def get_annotation_type(self):
        # Return the annotation type
        return self.annotation_type

    def get_available_info_fields(self):
        return self.info_fields

    def __unpack_snpeff_info(self, record):
        # Unpack the snpeff 'ANN' annotation field into the record info
        ann_info = record.INFO.pop("ANN")[0].split("|")
        # Convert empty string to NoneType
        ann_info = [None if x == "" else x for x in ann_info]
        # Add new annotations to dictionary
        for i in range(len(self.snpeff_info_fields)):
            record.INFO[self.snpeff_info_fields[i]] = ann_info[i]

    @staticmethod
    def calc_annotation_type(vcf_parser):
        # Determine the annotation format on a VCF file based on the info columns declared in the header
        if "ANN" in vcf_parser.infos:
            return VCFAnnotationType.SNPEFF
        elif "ANNOVAR_DATE" in vcf_parser.infos:
            return VCFAnnotationType.ANNOVAR
        else:
            return VCFAnnotationType.UNKNOWN
