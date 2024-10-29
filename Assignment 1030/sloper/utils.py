import numpy as np
import numpy.typing as npt
from   scipy import ndimage
import typing

class Utils():
    '''
    The unified interface for utility methods.
    '''
    
    def fill_nan(x: npt.NDArray) -> npt.NDArray:
        '''
        Fill NaN values in the DEM using the mean value of surrounding neighbors.

        Parameters
        --------
        x: NDArray
            The 2D numpy array consisting DEM data.

        Returns
        --------
        y: NDArray
            The numpy array with NaN values replaced by estimated heights.
        '''
        if not isinstance(x, np.ndarray):
            raise TypeError('The x must be a numpy array.')
        
        if x.ndim != 2:
            raise ValueError('The x must be a 2D array.')

        _x = x.copy()
        _win = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])

        # Check whether any cell contains NaN
        while np.isnan(_x).any():
            _real_neighbor_count = ndimage.convolve(1 - np.isnan(_x).astype(int), _win, mode = 'constant')
            _summation = ndimage.convolve(np.nan_to_num(_x), _win, mode = 'constant')
            _mask = np.isnan(_x) & (_real_neighbor_count > 1)
            with np.errstate(divide = 'ignore', invalid = 'ignore'):
                # Ignore divide by 0 and nan warnings
                np.putmask(_x, _mask, _summation / _real_neighbor_count)

        return _x

    def get_slope(fx: npt.ArrayLike,
                  fy: npt.ArrayLike,
                  format: typing.Literal['radian', 'degree', 'ratio'] = 'radian') -> npt.NDArray[np.float64] | np.float64:
        '''
        The utility helper function to get the slope efficiently.
        
        Parameters
        --------
        fx: ArrayLike
            The difference in x as an array.

        fy: ArrayLike
            The difference in y as an array.

        format: 'radian', 'degree', or 'ratio', optional
            The numeric representation of the slope. Default to be `'radian'`.

        Returns
        --------
        slope: NDArray[float64] | float64
            The slope in specified format as an array.
        '''
        if not isinstance(fx, (bool, int, float, complex, str, bytes, list, np.ndarray)):
            raise ValueError('The fx should be an ArrayLike object.')
        
        _fx: npt.NDArray[np.float64] = np.array(fx)

        if not isinstance(fy, (bool, int, float, complex, str, bytes, list, np.ndarray)):
            raise ValueError('The fy should be an ArrayLike object.')

        if not format in ['radian', 'degree', 'ratio']:
            raise ValueError(f'The format \'{format}\' is invalid; only \'radian\', \'degree\', or \'ratio\' are allowed.')
        
        _fy: npt.NDArray[np.float64] = np.array(fy)

        if _fx.shape != _fy.shape:
            raise ValueError('The shape is inconsistent between both arrays.')
        
        _slope = (_fx ** 2 + _fy ** 2) ** (1 / 2)

        match format:
            case 'degree':
                return np.arctan(_slope) * (180 / np.pi)

            case 'radian':
                return np.arctan(_slope)
            
            case 'ratio':
                return _slope