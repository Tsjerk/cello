import numpy as np
import matplotlib.pyplot as plt


def determine_kde_bw(values, hint=None, rule='scott'):
    """
    Determine bandwidth(s) for kernel density estimation.
    
    Parameters
    ----------
    values : array_like
        Input data. If 1-D, treated as single series. If 2-D, each row
        is a separate series.
    hint : None, float, 'global', 'local', or array_like, optional
        Bandwidth specification:
          - None: compute per-series bandwidth (equivalent to 'local')
          - float or int: use this value for all series
          - 'global': compute single bandwidth from all data combined
          - 'local': compute separate bandwidth for each series
          - array_like of length n: explicit bandwidth per series
    rule : {'scott', 'silverman'}, default='scott'
        Rule for automatic bandwidth calculation.
    
    Returns
    -------
    tuple of float
        Bandwidth values, one per series (or repeated if global/fixed).
    
    Raises
    ------
    ValueError
        If hint is an array with incorrect length or an unrecognized value.
    """
    values = np.asarray(values)
    
    ## Handle multiple series
    
    if values.ndim > 1:
        n = len(values)
        if hint is None or hint == 'global':
            # Global bandwidth: compute from all data
            return n*(determine_kde_bw(values.flatten(), None, rule), )
        elif hint == 'local':
            # Local bandwidth: compute per series (None or 'local')
            return tuple(determine_kde_bw(series, None, rule) for series in values)
        elif isinstance(hint, (float, int)):
            # Fixed bandwidth for all series
            return n*(hint, )
        elif isinstance(hint, (np.ndarray, list, tuple)) and len(hint) == n:
            # Explicit bandwidth per series
            return tuple(hint)
        raise ValueError(
            f"Invalid hint: {hint}. Must be a number, 'global', 'local', None, "
            f"or an array of length {n}."
        )
            
    ## Handle single series

    if isinstance(hint, (int, float)):
        return hint
    
    if rule == 'scott':
        return values.std() * values.size**(-1/5)
    elif rule == 'silverman':
        std = values.std()
        iqr = (np.percentile(values, 75) - np.percentile(values, 25)) / 1.349
        return (values.size * 3/4)**(-1/5) * min(std, iqr)
    raise ValueError(f"Unknown rule: {rule}. Use 'scott' or 'silverman'.")
        


def cello(values, c=None, position=None, basis=None, bw=None, cbw=None, scale=10, 
          points=100, horizontal=False, side='both', ax=None, **kwargs):
    """
    Draw a colored violin-like "cello" plot showing smoothed value distributions.

    The function computes a smoothed kernel-like density of the input values and
    visualizes it as a colored, optionally asymmetric shape. It can be called on a
    single 1-D array or a stack of arrays to generate grouped cello plots.

    Parameters
    ----------
    values : (n,) or (m, n) array_like
        Input data values. If 2-D, each row is treated as a separate group.
    c : None, str, tuple, or array_like, optional
        Color specification. May be:
          - None: default color cycle is used.
          - str: any Matplotlib color name or hex string.
          - tuple or list of length 3 or 4: single RGB(A) color.
          - (n, 3) or (n, 4) array: per-point RGB(A) colors.
          - (m, n, 3) array when `values` is 2-D: group-specific colors.
    position : float or sequence, optional
        Vertical (or horizontal, if `horizontal=True`) position(s) of the cello(s).
        Defaults to sequential positions starting at 1.
    basis : sequence, optional
        The basis for drawing the density, allowing stacked density plots.
    bw : float, default=0.5
        Bandwidth controlling the smoothness of the density.
    cbw : float, optional
        Optional color-bandwidth scaling; smaller values sharpen color transitions.
    scale : float, default=10
        Scaling factor for the density amplitude.
    points : int, default=100
        Number of points used to evaluate the smoothed density.
    horizontal : bool, default=False
        If True, the plot is oriented horizontally.
    side : {'both', 'left', 'right'}, default='both'
        Which side(s) of the cello to draw.
    ax : matplotlib.axes.Axes, optional
        Axes on which to draw. If None, uses the current axes.
    **kwargs
        Additional keyword arguments passed to the underlying Matplotlib
        plotting functions (e.g., `zorder`, `linewidth`, etc.).

    Returns
    -------
    dict
        For 1-D input:
            {
                'points' : ndarray of float
                    The grid points used for evaluating the density.
                'density' : ndarray of float
                    The normalized smoothed density values.
                'ax' : matplotlib.axes.Axes
                    The axes used for drawing.
                'mesh' : QuadMesh or None
                    The colored mesh artist, if drawn.
            }
        For 2-D input:
            {
                'group' : list of dict
                    The individual return dictionaries for each cello.
                'ax' : matplotlib.axes.Axes
                    The axes used for drawing.
            }

    Notes
    -----
    The density is normalized by the total kernel weight, ensuring that the
    overall area under the shape is unity (up to the scaling factor). This makes
    cellos visually comparable across groups regardless of sample size or bandwidth.

    Examples
    --------
    >>> data = np.random.randn(100)
    >>> cello(data, c='skyblue', position=1)

    >>> groups = [np.random.randn(100) + i for i in range(3)]
    >>> cello(np.array(groups), c='plasma', horizontal=True)
    """     

    ## Overall settings

    if ax is None:
        ax = plt.gca()

    bw = determine_kde_bw(values, bw, rule=kwargs.get('bwrule', 'scott'))
    if cbw is None:
        cbw = bw
    else:
        cbw = determine_kde_bw(values, cbw, rule=kwargs.get('bwrule', 'scott'))

    ## Processing cello ensemble
    
    # Handling array cello plots
    zorder = kwargs.pop('zorder', None)
    if values.ndim == 2:
        group = []
        colors = c
        pos = position
        for idx, vals in enumerate(values):
            if position is None:
                pos = idx + 1
            if isinstance(c, np.ndarray) and c.ndim == 3:
                colors = c[idx]
            zord = pos if zorder is None else zorder
            group.append(cello(
                vals, colors, position=pos, basis=basis, bw=bw[idx], cbw=cbw[idx],
                scale=scale, side=side, horizontal=horizontal, zorder=zord, ax=ax,
                **kwargs
            ))
            if basis is not None:
                basis = basis + group[-1]['density']
        return {'group': group, 'ax': ax}

    ## Processing solo cello
    
    # Color handling
    # a. No color (None); handled below
    # b. Named color (str)
    # c. Single color (3 or 4 tuple)
    # d. Color per value (n by 3-or-4 array)
    if c is not None:
        if (
                isinstance(c, str) or
                np.ndim(c) == 0 or
                (isinstance(c, (tuple, list)) and len(c) in (3, 4))
        ):
            from matplotlib.colors import to_rgba
            c = np.tile(to_rgba(c), (len(values), 1))
        
    # Single cello plot
    x = np.linspace(values.min() - 3*bw, values.max() + 3*bw, points)
    w = np.exp(-((x[:, None] - values[None, :])**2) / (bw**2))
    y = scale * w.sum(axis=1) / w.sum()  # normalized density
    if basis is not None:
        y += basis

    # Modify for ribbon
    xx = np.array([x, x])
    yy = (np.array([y, -y]).T * (1, side not in ('right', 'left'))).T
    if basis is not None:
        yy[1] = basis
        if side == 'left':
            pass
        elif side == 'right':
            yy = -yy
        else:
            xx = np.hstack([xx, xx[:, ::-1]])
            yy = np.hstack([yy, -yy[:, ::-1]])
    if position is not None:
        yy += position
    xx, yy = [xx, yy] if horizontal else [yy, xx] 
    
    # Plotting
    
    # - Body
    mesh = None
    if c is not None:
        if cbw is not None:
            w **= (bw/cbw)**2
        c = np.clip((w @ c) / w.sum(axis=1)[:, None], 0, 1)
        cc = np.array([c, c])
        if basis is not None:
            cc = np.hstack([c, c[::-1]])
        mesh = ax.pcolormesh(xx, yy, cc, shading='gouraud', zorder=zorder)

    # - Left line
    lines = []
    
    lines.append(ax.plot(xx[0,:len(x)], yy[0,:len(y)], c='k', linewidth=0.5, zorder=zorder))
    lines.append(ax.plot(xx[0,len(x):], yy[0,len(y):], c='k', linewidth=0.5, zorder=zorder))
    if basis is not None and side not in ('left', 'right'):
        lines.append(ax.plot(xx[0,:len(x)], yy[1,:len(y)], c='k', linewidth=0.5, zorder=zorder))
        lines.append(ax.plot(xx[0,:len(x)], yy[1,:len(y)], c='k', linewidth=0.5, zorder=zorder))
                 
                         
    #if side != 'right':
    #    xy = (x, position-y) if horizontal else (position-y, x)
    #    lines.append(ax.plot(*xy, c='k', linewidth=0.5, zorder=zorder))

    # - Right line
    #if side != 'left':
    #    xy = (x, position+y) if horizontal else (position+y, x)
    #    lines.append(ax.plot(*xy, c='k', linewidth=0.5, zorder=zorder))

    # - Base line, always marking the domain of the data
    xy = [[x.min(), x.max()], [position, position]]
    lines.append(ax.plot(xy[not horizontal], xy[horizontal], c='k', linewidth=0.5, zorder=zorder))
    xy = [[values.min(), values.max()], [position, position]]
    lines.append(ax.plot(xy[not horizontal], xy[horizontal], c='k', linewidth=2, zorder=zorder))
    
    return {'points': x, 'density': y, 'ax': ax, 'mesh': mesh}
