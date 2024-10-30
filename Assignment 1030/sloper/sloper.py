from __future__ import annotations

import numpy as np
import numpy.typing as npt
import os.path
import rasterio
import rasterio.transform
import sloper
import typing

class Dataset():
    '''
    The interface to perform slope calculations on given DEMs (mainly GeoTIFFs).
    '''

    # Initialization
    def __init__(self: Dataset, path: str | bytes | os.PathLike, **kwargs) -> None:
        '''
        Create an instance of `Dataset` from the file.

        Parameters
        --------
        path: str | bytes | os.PathLike
            The path to the DEM file. In order to process the data correctly, the file format should be stored under the logic of regular grids.

        band: int, optional
            The index of the band consisting the height values in the DEMs.
        '''
        self._band: int = 1
        self._distance: tuple
        self._extent: tuple[float, float, float, float]
        self._meta: dict = {}
        self._path: os.PathLike
        self._shape: tuple
        self._x: np.ndarray
        self._y: np.ndarray
        self._z: np.ndarray

        # Optional keyword arguments
        for k, v in kwargs.items():
            match k:
                case 'band':
                    if isinstance(v, int):
                        if v >= 1:
                            self._band = v

                        else:
                            raise ValueError('The band number is 1-indexed.')
                        
                    else:
                        raise TypeError('The band number should be an integer.')

        # Path argument
        if isinstance(path, (str, bytes, os.PathLike)):
            if os.path.isfile(path):
                try:
                    f: rasterio.DatasetReader
                    with rasterio.open(path) as f:
                        _band_info = f.read(self._band)
                        self._z = np.array(_band_info)  # Z (Height) array

                        _index_row, _index_col = np.meshgrid(np.arange(_band_info.shape[0]), np.arange(_band_info.shape[1]))
                        _coord_x, _coord_y = rasterio.transform.xy(f.transform, _index_col, _index_row)
                        self._x = np.reshape(_coord_x, self._z.shape)   # X array
                        self._y = np.reshape(_coord_y, self._z.shape)   # Y array
                        
                        self._distance = f.res
                        self._extent = (f.bounds.left, f.bounds.right, f.bounds.bottom, f.bounds.top)
                        self._meta = f.meta
                        self._shape = f.shape

                except Exception as e:
                    raise e
                
                finally:
                    self._path = path
                
            else:
                raise FileNotFoundError(f'The file doesn\'t exist: `{path}`')
            
        else:
            raise TypeError('The path should be a `str`, `bytes`, or `os.PathLike` object.')

    # Attributes
    __name__ = 'Dataset'

    # Properties
    @property
    def distance(self: Dataset) -> tuple[float, float]:
        '''
        The grid distance of the source file.
        '''
        return self._distance
    
    @distance.setter
    def distance(self: Dataset, new: typing.Any) -> None:
        raise AttributeError('The property `distance` is read-only.')
    
    @property
    def extent(self: Dataset) -> tuple[float, float, float, float]:
        '''
        The extent of the file in the format of (left, right, bottom, top).
        '''
        return self._extent
    
    @extent.setter
    def extent(self: Dataset, new: typing.Any) -> None:
        raise AttributeError('The property `extent` is read-only.')

    @property
    def meta(self: Dataset) -> dict | None:
        '''
        The source file's metadata.
        '''
        return self._meta
    
    @meta.setter
    def meta(self: Dataset, new: typing.Any) -> None:
        raise AttributeError('The property `meta` is read-only.')

    @property
    def path(self: Dataset) -> str | bytes | os.PathLike | None:
        '''
        The source file path of the `Dataset`.
        '''
        return self._path
    
    @path.setter
    def path(self: Dataset, new: typing.Any) -> None:
        raise AttributeError('The property `path` is read-only.')
    
    @property
    def x(self: Dataset) -> npt.NDArray:
        '''
        The array of each cell's x coordinate.
        '''
        return self._x
    
    @x.setter
    def x(self: Dataset, new: npt.NDArray) -> None:
        if isinstance(new, np.ndarray):
            if (new.shape == self._x.shape):
                self._x = new

            else:
                raise ValueError('The shape is inconsistent between both arrays.')
            
        else:
            raise TypeError('The x should be an `numpy.ndarray` object.')
        
    @property
    def y(self: Dataset) -> npt.NDArray:
        '''
        The array of each cell's y coordinate.
        '''
        return self._y
    
    @y.setter
    def y(self: Dataset, new: npt.NDArray) -> None:
        if isinstance(new, np.ndarray):
            if (new.shape == self._y.shape):
                self._y = new

            else:
                raise ValueError('The shape is inconsistent between both arrays.')
            
        else:
            raise TypeError('The y should be an `numpy.ndarray` object.')
        
    @property
    def z(self: Dataset) -> npt.NDArray:
        '''
        The array of each cell's z (height) value.
        '''
        return self._z
    
    @z.setter
    def z(self: Dataset, new: npt.NDArray) -> None:
        if isinstance(new, np.ndarray):
            if (new.shape == self._z.shape):
                self._z = new

            else:
                raise ValueError('The shape is inconsistent between both arrays.')
            
        else:
            raise TypeError('The z should be an `numpy.ndarray` object.')
        
    # Methods
    def slope(self: Dataset,
              method: int | typing.Literal['2FD', '3FDWRD', '3FD', '3FDWRSD', 'FFD', 'Maximum Max', 'Simple-D'],
              na_action: typing.Literal['fill'] | None = None,
              omit_edge: bool = False,
              format: typing.Literal['radian', 'degree', 'ratio'] = 'radian') -> np.ndarray:
        '''
        Calculate the slope based on the designated method.

        Parameters
        --------
        method: int | '2FD', '3FDWRD', '3FD', '3FDWRSD', 'FFD', 'Maximum Max', or 'Simple-D'
            The designated method to calculate the slope. The integer index for the limited option sequence is supported.

        na_action: 'fill' or None, optional
            The action taken to deal with NaN values. `'fill'` will replace NA values with the mean of its neighbors' heights, while `None` will do nothing.

        omit_edge: bool, optional
            Whether to omit the edge cells, default to be `False`. If the edge cells are computed, their unobserved neighbors' height will be their edge's height.

        format: 'radian', 'degree', or 'ratio'
            The numeric representation of the slope. Default to be `'radian'`.

        Returns
        --------
        slope: numpy.ndarray
            The slope of the dem.

        References
        --------
        Second-order Finite Difference (2FD)
            Flemming, M. D. and Hoffer, R. M. (1979)

        Three-order Finite Difference Weighted by Reciprocal Distance (3FDWRD)
            Unwin, D. (1981)

        Three-order Finite Difference, Linear Regression Plan (3FD)
            Sharpnack, D. A. and Akin, G. (1969)

        Three-order Finite Difference Weighted by Reciprocal of Squared Distance (3FDWRSD)
            Horn, B. K. P. (1981)

        Frame Finite Difference (FFD)
            T. H. Chu and T. H. Tsai (1995)

        Maximum Max
            Travis, M. R. E., Gary, H., Iverson, W. D. (1975); EPPL7 (1987)

        Simple Difference (Simple-D)
            Jones, K. H. (1998)
        '''
        _c1: np.ndarray
        _c2: np.ndarray
        _c3: np.ndarray
        _c4: np.ndarray
        _c5: np.ndarray
        _c6: np.ndarray
        _c7: np.ndarray
        _c8: np.ndarray
        _c9: np.ndarray
        _gd: float
        _gx: float
        _gy: float
        _method: str
        _Options = ['2FD', '3FDWRD', '3FD', '3FDWRSD', 'FFD', 'Maximum Max', 'Simple-D']
        _slope = np.ndarray

        if (self._x.shape != self._y.shape) | (self._x.shape != self._z.shape) | (self._y.shape != self._z.shape):
            raise ValueError('Inconsistent shape among arrays.')
        
        if isinstance(method, (int, str)):
            if isinstance(method, int):
                if (method >= 0) | (method <= 6):
                    _method = _Options[method]

                else:
                    raise ValueError('The method should be an `int` between 0 and 6.')
                
            else:
                if method in _Options:
                    _method = method

                else:
                    raise ValueError(f'The method \'{method}\' is invalid.')
        else:
            raise TypeError('The method can only be an `int` from 0 to 6 or literal option names.')
        
        if not na_action in ['fill', None]:
            raise TypeError('The na_action should be None or \'fill\'.')

        if not isinstance(omit_edge, bool):
            raise TypeError('The omit_edge should be a `bool` object (True/False).')

        if not format in ['radian', 'degree', 'ratio']:
            raise ValueError(f'The format \'{format}\' is invalid; only \'radian\', \'degree\', or \'ratio\' are allowed.')

        _gx = self._distance[0]
        _gy = self._distance[1]
        _gd = (_gx ** 2 + _gy ** 2) ** (1 / 2)
        _z = self._z

        if na_action == 'fill':
            _z = sloper.Utils.fill_nan(_z)

        _p = np.pad(_z, 1, 'edge')

        # Dynamically fill _c1 ~ _c9's value
        if _method not in ['2FD', 'Simple-D']:
            _c1 = _p[2:_p.shape[0]    , 2:_p.shape[1]]
            _c3 = _p[2:_p.shape[0]    , 0:_p.shape[1] - 2]
            _c7 = _p[0:_p.shape[0] - 2, 2:_p.shape[1]]
            _c9 = _p[0:_p.shape[0] - 2, 0:_p.shape[1] - 2]

        if _method not in ['FFD']:
            _c2 = _p[2:_p.shape[0]    , 1:_p.shape[1] - 1]
            _c4 = _p[1:_p.shape[0] - 1, 2:_p.shape[1]]

        if _method not in ['FFD', 'Simple-D']:
            _c6 = _p[1:_p.shape[0] - 1, 0:_p.shape[1] - 2]
            _c8 = _p[0:_p.shape[0] - 2, 1:_p.shape[1] - 1]

        if _method in ['Maximum Max', 'Simple-D']:
            _c5 = _p[1:_p.shape[0] - 1, 1:_p.shape[1] - 1]

        match _method:
            case '2FD':
                _slope = sloper.Utils.get_slope((_c6 - _c4) / (2 * _gx),
                                                (_c8 - _c2) / (2 * _gy),
                                                format)

            case '3FDWRD':
                _slope = sloper.Utils.get_slope((_c3 - _c1 + (2 ** (1 / 2)) * (_c6 - _c4) + _c9 - _c7) / ((4 + 8 ** (1 / 2)) * _gx),
                                                (_c7 - _c1 + (2 ** (1 / 2)) * (_c8 - _c2) + _c9 - _c3) / ((4 + 8 ** (1 / 2)) * _gy),
                                                format)

            case '3FD':
                _slope = sloper.Utils.get_slope((_c3 - _c1 + _c6 - _c4 + _c9 - _c7) / (6 * _gx),
                                                (_c7 - _c1 + _c8 - _c2 + _c9 - _c3) / (6 * _gy),
                                                format)

            case '3FDWRSD':
                _slope = sloper.Utils.get_slope((_c3 - _c1 + 2 * (_c6 - _c4) + _c9 - _c7) / (8 * _gx),
                                                (_c7 - _c1 + 2 * (_c8 - _c2) + _c9 - _c3) / (8 * _gy),
                                                format)

            case 'FFD':
                _slope = sloper.Utils.get_slope((_c3 - _c1 + _c9 - _c7) / (4 * _gx),
                                                (_c7 - _c1 + _c9 - _c3) / (4 * _gy),
                                                format)

            case 'Maximum Max':
                _s1 = np.abs((_c5 - _c1) / _gd)
                _s2 = np.abs((_c5 - _c2) / _gy)
                _s3 = np.abs((_c5 - _c3) / _gd)
                _s4 = np.abs((_c5 - _c4) / _gx)
                _s6 = np.abs((_c5 - _c6) / _gx)
                _s7 = np.abs((_c5 - _c7) / _gd)
                _s8 = np.abs((_c5 - _c8) / _gy)
                _s9 = np.abs((_c5 - _c9) / _gd)
                _slope = np.maximum.reduce([_s1, _s2, _s3, _s4, _s6, _s7, _s8, _s9])

                if format == 'degree':
                    _slope = np.arctan(_slope) * (180 / np.pi)

                if format == 'radian':
                    _slope = np.arctan(_slope)

            case 'Simple-D':
                _slope = sloper.Utils.get_slope((_c5 - _c4) / _gx,
                                                (_c5 - _c2) / _gy,
                                                format)

        if omit_edge:
            return _slope[1:-1, 1:-1]

        return _slope