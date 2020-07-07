# ThaiAddressParser  
![](https://img.shields.io/badge/language-python3-green.svg) ![](https://img.shields.io/badge/author-Shuai_Li-black.svg) ![](https://img.shields.io/badge/building-pass-yellow.svg) ![](https://img.shields.io/badge/license-MIT-pink.svg)      
`ThaiAddressParser` is a fast and unlimited python library which can deliver the structured Thailand address from the original free Thai sentence with translations.   
Meanwhile, it can extract the province, district, sub district from the original address sentence.
It is compatible with Python 3.  
This unique algorithm is developed by [the author](https://github.com/HandsomeBrotherShuaiLi)
## Feature  
* Fast (1.5 ms per sentence) 
* Stable (no external APIs)
* Easy to use and understand
* Robust
* Thread-safe
* Thai-En address Translation 
## Installation
For python3:
```angular2
pip3 install ThaiAddressParser
```
For python2:
```angular2
pip install ThaiAddressParser
```
## Usage
```angular2
>>> import ThaiAddressParser
>>> address = '7503 ถ.ราชญาวิริกษา ต.ม.ก่องคร อ.เมืองสมุทรสงคราม 10 จ.สมุทรสงคราม'
>>> ThaiAddressParser.parse(address)
{'original_address': '7503 ถ.ราชญาวิริกษา ต.ม.ก่องคร อ.เมืองสมุทรสงคราม 10 จ.สมุทรสงคราม', 'parsed_address': '7503 ถ.ราชญาวิริกษา ต.แม่กลอง อ.อุ้มผาง จ.ตาก', 'province': {'thai': 'ตาก', 'en': 'Tak'}, 'district': {'thai': 'อุ้มผาง', 'en': 'Umphang'}, 'sub_district': {'thai': 'แม่กลอง', 'en': 'Mae Klong'}, 'remaining_address': '7503 ถ.ราชญาวิริกษา'}
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


