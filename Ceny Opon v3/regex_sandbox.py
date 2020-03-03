import re

tyres_size = ['205/55R16 91 T MFS', '205/55R16 101 T',
              '205/55R16 91 H MFS', '205/55R16 91 T MFS,XL',
              '205/55R16 91 T,MFS,XL', '205/55R16 91 V MFS,XL Nowy bieżnik',
              '205/55R16 91 V MFS XL Nowy bieżnik', '205/55R16 91 T',
              '205/55R16 91 T', '205/55R16 91 H MFS']
tyres_size = [re.findall("\w+/\w+R\w+\s\w+\s\w+", size) for size in tyres_size]
tyres_size = sum(tyres_size, [])
tyres_size = [size[:-2]+size[-1:]  for size in tyres_size]
print(tyres_size)