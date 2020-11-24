import React, { useMemo } from 'react';

import { extractSortVideoAnnos } from '../../utils/extractSortVideoAnnos';

import { VideoAnno } from '../../store/shared/BaseShape';
import { isBBox } from '../../store/shared/Box2d';
import { isLine } from '../../store/shared/Line';
import { isPolygon } from '../../store/shared/Polygon';
import { CreatingState } from '../../store/videoAnnoSlice';
import { Box } from './Box';
import { Mask } from './Mask';
import { Polygon } from './Polygon';

type VideoAnnosGroupProps = {
  imgWidth: number;
  imgHeight: number;
  videoAnnos: VideoAnno[];
  updateVideoAnno: (id: string, changes) => void;
  removeVideoAnno: (id: string) => void;
  visible: boolean;
  creatingState: CreatingState;
  needMask: boolean;
  color?: string;
};

export const VideoAnnosGroup: React.FC<VideoAnnosGroupProps> = ({
  imgWidth,
  imgHeight,
  videoAnnos,
  updateVideoAnno,
  removeVideoAnno,
  visible,
  creatingState,
  needMask,
  color = 'white',
}): JSX.Element => {
  const enhanceSortVideoAnnos = useMemo(() => {
    return extractSortVideoAnnos(videoAnnos);
  }, [videoAnnos]) as VideoAnno[];

  console.log('enhanceSortVideoAnnos', enhanceSortVideoAnnos);

  return (
    <>
      {needMask && <Mask width={imgWidth} height={imgHeight} holes={videoAnnos} visible={visible} />}
      {enhanceSortVideoAnnos.map((e, videoAnnoIdx) => {
        if (isBBox(e)) {
          return (
            <Box
              key={e.id}
              box={{ ...e.vertices, id: e.id }}
              visible={visible}
              boundary={{ x1: 0, y1: 0, x2: imgWidth, y2: imgHeight }}
              onBoxChange={(changes): void => {
                updateVideoAnno(e.id, changes);
              }}
              removeBox={() => removeVideoAnno(e.id)}
              creatingState={creatingState}
              color={color}
            />
          );
        }
        if (isPolygon(e)) {
          return (
            <Polygon
              key={e.id}
              polygon={e.vertices}
              visible={visible}
              removePolygon={() => removeVideoAnno(e.id)}
              creatingState={creatingState}
              handleChange={(idx, vertex) => updateVideoAnno(e.id, { idx, vertex })}
              boundary={{ x1: 0, y1: 0, x2: imgWidth, y2: imgHeight }}
              color={color}
            />
          );
        }
        if (isLine(e)) {
          return (
            <Polygon
              key={e.id}
              polygon={e.vertices}
              visible={visible}
              removePolygon={() => removeVideoAnno(e.id)}
              creatingState={creatingState}
              handleChange={(idx, vertex) => updateVideoAnno(e.id, { idx, vertex })}
              boundary={{ x1: 0, y1: 0, x2: imgWidth, y2: imgHeight }}
              color={color}
              isLine
              lineIdx={videoAnnoIdx + 1}
            />
          );
        }
        return null;
      })}
    </>
  );
};
