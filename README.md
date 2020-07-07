# ThaiAddressParser  
![](https://img.shields.io/badge/language-python3-green.svg) ![](https://img.shields.io/badge/author-Shuai_Li-black.svg) ![](https://img.shields.io/badge/building-pass-yellow.svg) ![](https://img.shields.io/badge/license-MIT-pink.svg) ![](https://img.shields.io/badge/version-0.0.1-red.svg)    
`ThaiAddressParser` is a fast and unlimited python library which can deliver the structured Thailand address from the original free Thai sentence.   
Meanwhile, it can extract the province, district, sub district from the original address sentence.
It is compatible with Python 3.  
This unique algorithm is developed by [the author](https://github.com/HandsomeBrotherShuaiLi)
## Feature  
* Fast (1.5 ms per sentence) 
* Stable (no external APIs)
* Easy to use and understand
* Robust
* Thread-safe
## Installation
```angular2
pip install ThaiAddressParser
```
## Usage
```angular2
>>> import ThaiAddressParser
>>> address = '7503 ถ.ราชญาวิริกษา ต.ม.ก่องคร อ.เมืองสมุทรสงคราม 10 จ.สมุทรสงคราม'
>>> ThaiAddressParser.parse(address)
{'original_address': '7503 ถ.ราชญาวิริกษา ต.ม.ก่องคร อ.เมืองสมุทรสงคราม 10 จ.สมุทรสงคราม', 'parsed_address': '7503 ถ.ราชญาวิริกษา ต.แม่กลอง อ.อุ้มผาง จ.ตาก', 'province': 'ตาก', 'district': 'อุ้มผาง', 'sub_district': 'แม่กลอง', 'remaining_address': '7503 ถ.ราชญาวิริกษา'}
>>> address = '263 หมู่ที่ 1 ต.นาซาว อ.เชียงคาน จ.เลย'
>>> ThaiAddressParser.parse(address)
{'original_address': '263 หมู่ที่ 1 ต.นาซาว อ.เชียงคาน จ.เลย', 'parsed_address': '263 หมู่ที่ 1 ต.นาซ่าว อ.เชียงคาน จ.เลย', 'province': 'เลย', 'district': 'เชียงคาน', 'sub_district': 'นาซ่าว', 'remaining_address': '263 หมู่ที่ 1'}
>>> address = '1 2001 00037 15'
>>> ThaiAddressParser.parse(address)
{'original_address': '1 2001 00037 15', 'parsed_address': 'null', 'province': 'null', 'district': 'null', 'sub_district': 'null', 'remaining_address': 'null'}
```

## License
```angular2
MIT License

Copyright (c) 2020 Shuai Li

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```


